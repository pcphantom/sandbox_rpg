"""Utility functions — noise, math helpers."""
import math


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(v: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, v))


def hash_noise(x: int, y: int, seed: int) -> float:
    n = (x * 374761393 + y * 668265263 + seed * 374761393) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0x7FFFFFFF) / 0x7FFFFFFF


def value_noise_2d(x: float, y: float, seed: int) -> float:
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    v00 = hash_noise(ix, iy, seed)
    v10 = hash_noise(ix + 1, iy, seed)
    v01 = hash_noise(ix, iy + 1, seed)
    v11 = hash_noise(ix + 1, iy + 1, seed)
    sx = fx * fx * (3 - 2 * fx)
    sy = fy * fy * (3 - 2 * fy)
    return lerp(lerp(v00, v10, sx), lerp(v01, v11, sx), sy)


def fbm_noise(x: float, y: float, seed: int, octaves: int = 4) -> float:
    total, amp, freq, mx = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += value_noise_2d(x * freq, y * freq, seed) * amp
        mx += amp
        amp *= 0.5
        freq *= 2.0
    return total / mx
