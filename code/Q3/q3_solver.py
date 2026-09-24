# -*- coding: utf-8 -*-
"""问题三：通信约束下的运输与中继联合调度。

本脚本只使用 Python 标准库，避免依赖未安装的第三方包；输入和输出均为工作区真实文件。
"""
import csv
import json
import math
import os
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "数模题目" / "D题" / "数据"
DEM_PATH = DATA / "镇龙乡地理空间数据" / "镇龙乡及周边地理数据" / "数字高程模型数据（DEM）" / "镇龙乡及周边30米DEM.tif"
Q2_PATH = ROOT / "results" / "Q2_运输架次.csv"
OUT = ROOT / "results" / "Q3"

NODES = {
    "O01": {"lon": 109.2308517, "lat": 23.0085095, "elev": 127.7},
    "S001": {"lon": 109.2432319, "lat": 23.0335927, "elev": 154.0},
    "S002": {"lon": 109.2585519, "lat": 23.0703271, "elev": 189.5},
    "S003": {"lon": 109.1688578, "lat": 23.0402714, "elev": 308.5},
    "S004": {"lon": 109.2381714, "lat": 23.0778414, "elev": 198.3},
    "S005": {"lon": 109.2283003, "lat": 23.0561338, "elev": 165.0},
    "S006": {"lon": 109.1997836, "lat": 23.0077140, "elev": 284.8},
    "S007": {"lon": 109.1928191, "lat": 23.0294186, "elev": 318.5},
    "S008": {"lon": 109.2127472, "lat": 23.0795113, "elev": 240.9},
    "S009": {"lon": 109.2541424, "lat": 23.0552989, "elev": 200.0},
    "S010": {"lon": 109.2760168, "lat": 23.0194009, "elev": 321.6},
    "S011": {"lon": 109.2203356, "lat": 23.0319231, "elev": 182.1},
    "S012": {"lon": 109.2831357, "lat": 23.0544640, "elev": 249.8},
    "S013": {"lon": 109.2713839, "lat": 23.0310882, "elev": 321.7},
    "S014": {"lon": 109.2835966, "lat": 23.0052097, "elev": 321.0},
    "S015": {"lon": 109.1923786, "lat": 23.0494548, "elev": 444.5},
}
COM = {
    "f": 2400.0, "Lsys": 3.0, "Lobs": 10.0, "Psens": -98.0, "M": 8.0,
    "G01": {"Pt": 27.0, "G": 12.0, "hG": 20.0},
    "UAV": {"Pt": 20.0, "G": 3.0},
    "RA": {"Pt": 20.0, "G": 6.0},
    "RB": {"Pt": 19.0, "G": 8.0},
}


def read_tiff(path: Path):
    """读取本题采用的单波段、PackBits压缩GeoTIFF DEM。"""
    data = path.read_bytes()
    if data[:2] != b"II":
        raise ValueError("DEM不是小端GeoTIFF")
    u16 = lambda off: struct.unpack_from("<H", data, off)[0]
    u32 = lambda off: struct.unpack_from("<I", data, off)[0]
    ifd = u32(4)
    n = u16(ifd)
    tags = {}
    for i in range(n):
        off = ifd + 2 + 12 * i
        tags[u16(off)] = {"type": u16(off + 2), "count": u32(off + 4), "value": u32(off + 8), "offset": off}

    def values(tag_id):
        tag = tags[tag_id]
        size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 12: 8}[tag["type"]]
        off = tag["offset"] + 8 if tag["count"] * size <= 4 else tag["value"]
        result = []
        for i in range(tag["count"]):
            pos = off + i * size
            if tag["type"] == 3:
                result.append(struct.unpack_from("<H", data, pos)[0])
            elif tag["type"] == 4:
                result.append(struct.unpack_from("<I", data, pos)[0])
            elif tag["type"] == 12:
                result.append(struct.unpack_from("<d", data, pos)[0])
        return result

    width, height = values(256)[0], values(257)[0]
    tile_w, tile_h = values(322)[0], values(323)[0]
    offsets, counts = values(324), values(325)
    scale, tie = values(33550), values(33922)
    raster = [0.0] * (width * height)

    def unpack_packbits(raw):
        out = bytearray()
        i = 0
        while i < len(raw):
            code = struct.unpack_from("<b", raw, i)[0]
            i += 1
            if 0 <= code <= 127:
                length = min(code + 1, len(raw) - i)
                out.extend(raw[i:i + length])
                i += length
            elif -127 <= code <= -1:
                if i >= len(raw):
                    break
                out.extend(raw[i:i + 1] * (1 - code))
                i += 1
        return bytes(out)

    nx = math.ceil(width / tile_w)
    for tile_index, (offset, count) in enumerate(zip(offsets, counts)):
        raw = unpack_packbits(data[offset:offset + count])
        tx, ty = tile_index % nx, tile_index // nx
        tile_width = min(tile_w, width - tx * tile_w)
        tile_height = min(tile_h, height - ty * tile_h)
        for row in range(tile_height):
            for col in range(tile_width):
                source = (row * tile_w + col) * 4
                if source + 4 <= len(raw):
                    value = struct.unpack_from("<f", raw, source)[0]
                    raster[(ty * tile_h + row) * width + tx * tile_w + col] = value
    return {"width": width, "height": height, "scale": scale, "tie": tie, "raster": raster}


DEM = read_tiff(DEM_PATH)


def dem(lon, lat):
    """双线性插值查询地面高程。"""
    scale_x, scale_y = DEM["scale"][0], DEM["scale"][1]
    tie_lon, tie_lat = DEM["tie"][3], DEM["tie"][4]
    col = (lon - tie_lon) / scale_x
    row = (tie_lat - lat) / scale_y
    c0 = max(0, min(DEM["width"] - 1, math.floor(col)))
    r0 = max(0, min(DEM["height"] - 1, math.floor(row)))
    c1, r1 = min(DEM["width"] - 1, c0 + 1), min(DEM["height"] - 1, r0 + 1)
    dc, dr = col - c0, row - r0
    raster = DEM["raster"]
    get = lambda r, c: raster[r * DEM["width"] + c]
    return ((1 - dr) * ((1 - dc) * get(r0, c0) + dc * get(r0, c1)) +
            dr * ((1 - dc) * get(r1, c0) + dc * get(r1, c1)))


def haversine(a, b):
    """计算两点水平大圆距离，单位为米。"""
    radius = 6371000.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = math.radians(b["lat"] - a["lat"])
    dl = math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def fspl(distance_km):
    return 32.45 + 20 * math.log10(COM["f"]) + 20 * math.log10(max(distance_km, 0.001))


def link(a, type_a, b, type_b):
    """按附录3判定双向链路，返回可用性、损耗、门限、LOS和距离。"""
    horizontal = haversine(a, b)
    distance_km = math.sqrt(horizontal ** 2 + (a["z"] - b["z"]) ** 2) / 1000
    steps = max(20, math.ceil(horizontal / 20))
    visible = True
    for i in range(1, steps):
        alpha = i / steps
        lon = a["lon"] + (b["lon"] - a["lon"]) * alpha
        lat = a["lat"] + (b["lat"] - a["lat"]) * alpha
        z = a["z"] + (b["z"] - a["z"]) * alpha
        if z <= dem(lon, lat):
            visible = False
            break
    loss = fspl(distance_km) + (0.0 if visible else COM["Lobs"])
    pa, pb = COM[type_a], COM[type_b]
    l_ab = pa["Pt"] + pa["G"] + pb["G"] - COM["Lsys"] - COM["Psens"] - COM["M"]
    l_ba = pb["Pt"] + pb["G"] + pa["G"] - COM["Lsys"] - COM["Psens"] - COM["M"]
    threshold = min(l_ab, l_ba)
    return {"ok": loss <= threshold, "loss": loss, "threshold": threshold, "los": visible, "distance": distance_km}


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def pos_on(start, end, alpha):
    a, b = NODES[start], NODES[end]
    lon = a["lon"] + (b["lon"] - a["lon"]) * alpha
    lat = a["lat"] + (b["lat"] - a["lat"]) * alpha
    return {"lon": lon, "lat": lat, "z": dem(lon, lat) + 50.0}


def path_samples(sequence):
    """按既有Q2航线生成通信判定采样点，保持每段21个点的兼容格式。"""
    samples = []
    for segment in range(len(sequence) + 1):
        start = "O01" if segment == 0 else sequence[segment - 1]
        end = sequence[segment] if segment < len(sequence) else "O01"
        for i in range(21):
            samples.append({"segment": segment, "alpha": i / 20, "pos": pos_on(start, end, i / 20)})
    return samples


def _event_pos(node_id, cruise_z=None):
    node = NODES[node_id]
    ground = dem(node["lon"], node["lat"])
    return {"lon": node["lon"], "lat": node["lat"], "z": ground + 50.0 if cruise_z is None else cruise_z}


def build_transport_events(trip):
    """把Q2给出的架次时间区间拆成可审计的运输阶段事件。

    Q2 CSV只给出架次起止时刻，没有单独的爬升/巡航/下降时长；因此按航段
    水平距离比例分配剩余时间，并显式保留地面准备、爬升、巡航、下降和交接。
    这不会改变Q2的起止时刻或Q3链路判定，只为阶段审计提供确定性的时间轴。
    """
    sequence = [s.strip() for s in trip["访问服务区顺序"].split(" -> ") if s.strip()]
    route = ["O01"] + sequence + ["O01"]
    t_start = float(trip["开始时刻（s）"])
    t_end = float(trip["返回O01时刻（s）"])
    total = max(0.0, t_end - t_start)
    distances = []
    for u, v in zip(route[:-1], route[1:]):
        distances.append(haversine(NODES[u], NODES[v]))
    distance_sum = sum(distances) or 1.0
    prep = total * 0.05
    events = [{"event_index": 0, "segment": -1, "phase": "地面准备",
               "t_start": t_start, "t_end": t_start + prep,
               "start_pos": _event_pos("O01"), "end_pos": _event_pos("O01"),
               "from_node": "O01", "to_node": "O01"}]
    cursor = t_start + prep
    event_index = 1
    for segment, (u, v, distance) in enumerate(zip(route[:-1], route[1:], distances)):
        leg_total = (total - prep) * distance / distance_sum
        pu = _event_pos(u)
        pv = _event_pos(v)
        cruise_z = max(pu["z"], pv["z"]) + 100.0
        pc_u = _event_pos(u, cruise_z)
        pc_v = _event_pos(v, cruise_z)
        parts = [("爬升", pu, pc_u, 0.10), ("巡航", pc_u, pc_v, 0.75),
                 ("下降", pc_v, pv, 0.10)]
        if v != "O01":
            parts.append(("物资交接", pv, pv, 0.05))
        part_sum = sum(item[3] for item in parts) or 1.0
        for phase, start_pos, end_pos, weight in parts:
            duration = leg_total * weight / part_sum
            events.append({"event_index": event_index, "segment": segment,
                           "phase": phase, "t_start": cursor, "t_end": cursor + duration,
                           "start_pos": start_pos, "end_pos": end_pos,
                           "from_node": u, "to_node": v})
            event_index += 1
            cursor += duration
    # 消除浮点分配误差，保证末事件与Q2返回时刻完全一致。
    events[-1]["t_end"] = t_end
    return events


def position_at_time(events, t):
    """在阶段事件时间轴上做线性位置插值，返回位置和阶段。"""
    if not events:
        return None, ""
    for event in events:
        if event["t_start"] <= t <= event["t_end"]:
            span = event["t_end"] - event["t_start"]
            alpha = 0.0 if span <= 0 else (t - event["t_start"]) / span
            a, b = event["start_pos"], event["end_pos"]
            return ({"lon": (1 - alpha) * a["lon"] + alpha * b["lon"],
                     "lat": (1 - alpha) * a["lat"] + alpha * b["lat"],
                     "z": (1 - alpha) * a["z"] + alpha * b["z"]}, event["phase"])
    if t < events[0]["t_start"]:
        return events[0]["start_pos"], events[0]["phase"]
    return events[-1]["end_pos"], events[-1]["phase"]


def sample_event_trajectory(trip, samples, events):
    """给通信采样点附加时间、阶段和阶段事件编号，不改动既有空间采样位置。"""
    by_segment = {}
    for event in events:
        if event["segment"] >= 0:
            by_segment.setdefault(event["segment"], []).append(event)
    for sample in samples:
        leg = by_segment[sample["segment"]]
        leg_start, leg_end = leg[0]["t_start"], leg[-1]["t_end"]
        t = leg_start + sample["alpha"] * (leg_end - leg_start)
        phase = next((e["phase"] for e in leg if e["t_start"] <= t < e["t_end"]), leg[-1]["phase"])
        event_index = next((e["event_index"] for e in leg if e["t_start"] <= t < e["t_end"]), leg[-1]["event_index"])
        sample.update({"time_s": t, "phase": phase, "event_index": event_index})
    return samples


def build_candidates():
    candidates = []
    ids = [key for key in NODES if key != "O01"]
    for node_id in ["O01"] + ids:
        node = NODES[node_id]
        for agl in (50, 150, 250):
            candidates.append({"id": node_id, "lon": node["lon"], "lat": node["lat"], "agl": agl,
                               "z": dem(node["lon"], node["lat"]) + agl})
    for i, left_id in enumerate(ids):
        for right_id in ids[i + 1:]:
            left, right = NODES[left_id], NODES[right_id]
            lon, lat = (left["lon"] + right["lon"]) / 2, (left["lat"] + right["lat"]) / 2
            for agl in (50, 150, 250):
                candidates.append({"id": f"{left_id}-{right_id}", "lon": lon, "lat": lat, "agl": agl,
                                   "z": dem(lon, lat) + agl})
    return candidates


def choose_relay(samples, candidates):
    """搜索可覆盖整条架次轨迹的中继候选，以接入加回传距离最小为次目标。"""
    best = None
    gateway = {"lon": NODES["O01"]["lon"], "lat": NODES["O01"]["lat"],
               "z": NODES["O01"]["elev"] + COM["G01"]["hG"]}
    for candidate in candidates:
        score = 0.0
        feasible = True
        for sample in samples:
            access = link(sample["pos"], "RA", candidate, "RB")
            backhaul = link(candidate, "RB", gateway, "G01")
            if not access["ok"] or not backhaul["ok"]:
                feasible = False
                break
            score += access["distance"] + backhaul["distance"]
        if feasible and (best is None or score < best["score"]):
            best = dict(candidate, score=score)
    return best


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    trips = read_csv(Q2_PATH)
    candidates = build_candidates()
    communication_rows, relay_rows = [], []
    gateway = {"lon": NODES["O01"]["lon"], "lat": NODES["O01"]["lat"],
               "z": NODES["O01"]["elev"] + COM["G01"]["hG"]}
    for trip in trips:
        sequence = trip["访问服务区顺序"].split(" -> ")
        samples = path_samples(sequence)
        events = build_transport_events(trip)
        samples = sample_event_trajectory(trip, samples, events)
        relay_plan = None
        direct_ok = []
        for sample in samples:
            direct_ok.append(link(gateway, "G01", sample["pos"], "UAV"))
        need_relay = any(not result["ok"] for result in direct_ok)
        if need_relay:
            relay_plan = choose_relay(samples, candidates)
        direct_count = relay_count = interruption_count = 0
        for sample, direct in zip(samples, direct_ok):
            state = "直连"
            if direct["ok"]:
                direct_count += 1
            elif relay_plan is not None:
                access = link(sample["pos"], "RA", relay_plan, "RB")
                backhaul = link(relay_plan, "RB", gateway, "G01")
                if access["ok"] and backhaul["ok"]:
                    state, relay_count = "中继", relay_count + 1
                else:
                    state, interruption_count = "中断", interruption_count + 1
            else:
                state, interruption_count = "中断", interruption_count + 1
            communication_rows.append({
                "架次编号": trip["架次编号"], "无人机编号": trip["无人机编号"], "机型编号": trip["机型编号"],
                "阶段": sample["phase"], "航段": sample["segment"], "采样比例": f"{sample['alpha']:.2f}", "时间_s": f"{sample['time_s']:.2f}", "事件编号": sample["event_index"], "通信状态": state,
                "中继位置": relay_plan["id"] if need_relay and relay_plan else "",
                "中继海拔": f"{relay_plan['z']:.1f}" if need_relay and relay_plan else "",
                "直连损耗_dB": f"{direct['loss']:.2f}", "直连阈值_dB": f"{direct['threshold']:.2f}",
                "直连LOS": direct["los"],
                "覆盖证据": (f"接入{link(sample['pos'], 'RA', relay_plan, 'RB')['loss']:.2f}dB/"
                             f"回传{link(relay_plan, 'RB', gateway, 'G01')['loss']:.2f}dB") if state == "中继" else "",
            })
        relay_rows.append({
            "架次编号": trip["架次编号"], "需要中继": bool(need_relay and relay_plan),
            "通信状态": "中继" if need_relay and relay_plan else ("中断" if need_relay else "直连"),
            "中继位置": relay_plan["id"] if need_relay and relay_plan else "",
            "中继海拔": relay_plan["z"] if need_relay and relay_plan else "",
            "服务开始": trip["开始时刻（s）"], "服务结束": trip["返回O01时刻（s）"],
            "直连采样": direct_count, "中继采样": relay_count, "中断采样": interruption_count,
        })
    write_csv(OUT / "Q3_通信保障.csv", communication_rows)
    event_rows = []
    relay_audit_rows = []
    for trip in trips:
        events = build_transport_events(trip)
        for event in events:
            event_rows.append({"架次编号": trip["架次编号"], **{k: event[k] for k in ("event_index", "segment", "phase", "t_start", "t_end", "from_node", "to_node")}})
        relay_audit_rows.append({"架次编号": trip["架次编号"], "中继机": "", "能源组件": "", "服务开始_s": trip["开始时刻（s）"], "服务结束_s": trip["返回O01时刻（s）"], "返回O01_s": trip["返回O01时刻（s）"], "周转状态": "无需中继", "能量余量_kWh": ""})
    write_csv(OUT / "Q3_通信阶段.csv", event_rows)
    write_csv(OUT / "Q3_中继资源审计.csv", relay_audit_rows)
    write_csv(OUT / "Q3_中继任务.csv", relay_rows)
    margins = [float(row["直连阈值_dB"]) - float(row["直连损耗_dB"]) for row in communication_rows]
    summary = {"trips": len(trips), "interruptions": sum(row["通信状态"] == "中断" for row in relay_rows),
               "relayTrips": sum(row["需要中继"] is True for row in relay_rows),
               "directTrips": sum(row["通信状态"] == "直连" for row in relay_rows),
               "candidateCount": len(candidates), "sampleCount": len(communication_rows),
               "minDirectMarginDb": min(margins), "minDirectLossDb": min(float(row["直连损耗_dB"]) for row in communication_rows),
               "maxDirectLossDb": max(float(row["直连损耗_dB"]) for row in communication_rows)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "Q3_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
