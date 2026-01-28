
import math

def best_atlas_grid(
    N,
    W_max, H_max,
    W_src, H_src,
    priority="horizontal",   # or "area"
    align=2                  # align to multiple of 2 (HEVC safe)
):
    aspect = W_src / H_src
    best = None

    # tester toutes les grilles possibles
    for C in range(1, N + 1):
        R = math.ceil(N / C)

        # taille max possible par tuile
        W_tile_max = W_max // C
        H_tile_max = H_max // R

        if W_tile_max <= 0 or H_tile_max <= 0:
            continue

        # respecter l'aspect ratio source
        H_view = min(H_tile_max, int(W_tile_max / aspect))
        W_view = int(H_view * aspect)

        # ne jamais upscaler
        W_view = min(W_view, W_src)
        H_view = min(H_view, H_src)

        # alignement codec (pair / multiple de 8 si tu veux)
        W_view = (W_view // align) * align
        H_view = (H_view // align) * align

        if W_view <= 0 or H_view <= 0:
            continue

        # atlas final
        W_atlas = W_view * C
        H_atlas = H_view * R

        if W_atlas > W_max or H_atlas > H_max:
            continue

        # score
        if priority == "horizontal":
            score = W_view
        else:
            score = W_view * H_view

        candidate = {
            "C": C,
            "R": R,
            "W_view": W_view,
            "H_view": H_view,
            "W_atlas": W_atlas,
            "H_atlas": H_atlas,
            "score": score
        }

        if best is None or score > best["score"]:
            best = candidate

    return best

if __name__ == "__main__":
    # test
    N = 24
    W_max = 8192
    H_max = 4320
    W_src = 1920
    H_src = 1080

    result = best_atlas_grid(N, W_max, H_max, W_src, H_src, priority="horizontal", align=2)
    print(result)