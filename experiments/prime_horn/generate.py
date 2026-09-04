#!/usr/bin/env python3
"""Generate a smooth, watertight prime-radius horn as STL plus inspection files."""

from __future__ import annotations

import csv
import json
import math
import struct
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PRIMES = np.asarray([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=float)
HEIGHTS = np.arange(len(PRIMES), dtype=float)
NZ = 200
NTHETA = 128
WALL = 0.40


def profile():
    z = np.linspace(HEIGHTS[0], HEIGHTS[-1], NZ)
    r = PchipInterpolator(HEIGHTS, PRIMES)(z)
    if np.any(np.diff(r) < -1e-12):
        raise RuntimeError("monotone interpolation check failed")
    return z, r


def ring_vertices(z, radii):
    theta = np.linspace(0.0, 2.0 * math.pi, NTHETA, endpoint=False)
    rings = []
    for zz, rr in zip(z, radii):
        rings.append(np.column_stack((rr * np.cos(theta), rr * np.sin(theta), np.full_like(theta, zz))))
    return np.asarray(rings)


def build_mesh(z, outer_r):
    inner_r = np.maximum(outer_r - WALL, 0.05)
    outer = ring_vertices(z, outer_r)
    inner = ring_vertices(z, inner_r)
    vertices = np.concatenate((outer.reshape(-1, 3), inner.reshape(-1, 3)), axis=0)
    inner_offset = NZ * NTHETA
    faces = []

    for iz in range(NZ - 1):
        for it in range(NTHETA):
            jt = (it + 1) % NTHETA
            a, b = iz * NTHETA + it, iz * NTHETA + jt
            c, d = (iz + 1) * NTHETA + it, (iz + 1) * NTHETA + jt
            faces.extend(((a, c, d), (a, d, b)))
            ai, bi, ci, di = inner_offset + a, inner_offset + b, inner_offset + c, inner_offset + d
            faces.extend(((ai, di, ci), (ai, bi, di)))

    for iz, reverse in ((0, True), (NZ - 1, False)):
        for it in range(NTHETA):
            jt = (it + 1) % NTHETA
            a, b = iz * NTHETA + it, iz * NTHETA + jt
            ai, bi = inner_offset + a, inner_offset + b
            faces.extend(((a, bi, ai), (a, b, bi)) if reverse else ((a, ai, bi), (a, bi, b)))
    return vertices, np.asarray(faces, dtype=np.int32)


def write_binary_stl(path, vertices, faces):
    with path.open("wb") as handle:
        handle.write(b"Smooth prime horn; PCHIP profile; units arbitrary".ljust(80, b" "))
        handle.write(struct.pack("<I", len(faces)))
        for face in faces:
            tri = vertices[face]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            norm = np.linalg.norm(normal)
            normal = normal / norm if norm else normal
            handle.write(struct.pack("<12fH", *(normal.tolist() + tri.reshape(-1).tolist()), 0))


def manifold_edge_check(faces):
    counts = {}
    for face in faces:
        for a, b in zip(face, np.roll(face, -1)):
            edge = tuple(sorted((int(a), int(b))))
            counts[edge] = counts.get(edge, 0) + 1
    values = np.asarray(list(counts.values()))
    return {"unique_edges": len(counts), "all_edges_have_two_faces": bool(np.all(values == 2)), "min_faces_per_edge": int(values.min()), "max_faces_per_edge": int(values.max())}


def render_png(path, z, r):
    theta = np.linspace(0.0, 2.0 * math.pi, 144)
    tt, zz = np.meshgrid(theta, z)
    rr = r[:, None]
    xx, yy = rr * np.cos(tt), rr * np.sin(tt)
    fig = plt.figure(figsize=(10, 7), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(xx, yy, zz, cmap="plasma", edgecolor="none", alpha=0.92)
    for h, radius in zip(HEIGHTS, PRIMES):
        ax.plot(radius * np.cos(theta), radius * np.sin(theta), np.full_like(theta, h), color="white", linewidth=0.8, alpha=0.75)
    ax.set(xlabel="x", ylabel="y", zlabel="height", title="Smooth prime horn — prime radii at unit-spaced heights")
    ax.set_box_aspect((2.0, 2.0, 1.15))
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    z, r = profile()
    vertices, faces = build_mesh(z, r)
    write_binary_stl(OUT / "prime_horn.stl", vertices, faces)
    render_png(OUT / "prime_horn.png", z, r)
    with (OUT / "profile.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("height", "radius"))
        writer.writerows(zip(z, r))
    metrics = {
        "prime_radii": PRIMES.astype(int).tolist(),
        "heights": HEIGHTS.astype(int).tolist(),
        "interpolation": "PCHIP (monotone piecewise cubic Hermite)",
        "wall_thickness": WALL,
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "radius_min": float(r.min()),
        "radius_max": float(r.max()),
        "monotone_profile": bool(np.all(np.diff(r) >= -1e-12)),
        "mesh": manifold_edge_check(faces),
        "claim_boundary": "data sculpture only; acoustic eigenfrequencies not computed",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
