"""examples/prismatics_backend_example.py

Prototype example showing how to consume Prismatics operations and pack the
`index` payload into a uniform-like structure and the `scatter` points into a
simple vertex buffer suitable for upload to a GPU (OpenGL / Vulkan / WebGL).

The file demonstrates two modes:
 - pure-data mode: show how to convert index/scatter into contiguous numpy
   arrays and a small uniform dict (safe to run in CI / headless environments)
 - optional GL mode: if `moderngl` is available and a context can be created,
   create GPU buffers and show the minimal shader inputs you'd use.

This is a prototype for illustration and is intentionally backend-neutral. Use
it as a starting point for real backends that create SSBOs/UBOs or push
constants/pipeline layouts for Vulkan/GL/WebGPU.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

from boa_bigapi.prismatics import Prismatics


# --- Helpers for packing data ---

def pack_index_to_uniforms(index_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert `index` payload into a uniform-like dict suitable for GPU upload.

    The returned dict emulates the small uniform block a shader would consume.
    Values are primitive Python floats/ints or numpy scalars when numpy is
    available (easier for real GPU library bindings).
    """
    r = float(index_payload.get("r_mean", 0.0))
    g = float(index_payload.get("g_mean", 0.0))
    b = float(index_payload.get("b_mean", 0.0))
    golden = index_payload.get("golden_lengths", {})
    short = float(golden.get("short", 1.0))
    middle = float(golden.get("middle", 1.61803398875))
    long_ = float(golden.get("long", 2.61803398875))
    scale = float(golden.get("scale_factor", 1.0))

    # Derived rotation angles (degrees) -> convert to radians for GPU
    derived = index_payload.get("derived", {})
    pitch_deg = float(derived.get("pitch_deg", 0.0))
    roll_deg = float(derived.get("roll_deg", 0.0))

    # Convert to radians for shader convenience
    import math

    pitch_rad = math.radians(pitch_deg)
    roll_rad = math.radians(roll_deg)

    uniforms = {
        "u_r_mean": r,
        "u_g_mean": g,
        "u_b_mean": b,
        "u_golden_short": short,
        "u_golden_middle": middle,
        "u_golden_long": long_,
        "u_scale_factor": scale,
        "u_pitch_rad": pitch_rad,
        "u_roll_rad": roll_rad,
    }

    # If numpy is present, convert to numpy scalars for easier buffer uploads
    if np is not None:
        uniforms = {k: np.float32(v) for k, v in uniforms.items()}

    return uniforms


def pack_scatter_to_vertex_buffer(scatter_points: List[Tuple[float, float, int]], dtype: str = "f4"):
    """Pack scatter points into a contiguous vertex buffer.

    Each vertex will be: [x_norm(float), y_norm(float), channel(float/int)]
    Return a numpy array (if numpy available) or a bytes object for upload.
    """
    # Flatten to Nx3
    if scatter_points is None:
        scatter_points = []
    data = []
    for x, y, ch in scatter_points:
        data.append((float(x), float(y), float(ch)))

    if np is None:
        # Minimal pure-python packing into bytes (little-endian float32)
        import struct

        packed = b"".join(struct.pack("<fff", *triple) for triple in data)
        return packed

    arr = np.array(data, dtype=np.float32)
    # Some GL APIs prefer tightly packed float32 arrays; others use interleaved
    return arr


# --- Example backend consumer ---

class ExampleGPUBackend:
    """Prototype backend showing how to consume Prismatics operations and
    prepare GPU-friendly objects.

    This backend does not require a GL context. The `prepare_gpu_objects`
    method returns a dict describing the uniform block and vertex buffer(s).

    The optional `upload_to_moderngl` demonstrates how to create GPU buffers
    if a moderngl context is available.
    """

    def __init__(self):
        # In a real backend you would keep references to created buffers
        self.uniforms = None
        self.vertex_buffer = None

    def prepare_gpu_objects(self, operations: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """Scan the operations and create uniform / vertex buffer representations.

        Returns a dict with keys: 'uniforms' and 'scatter_buffer' (numpy arr or bytes)
        """
        index_payload = None
        scatter_points = None
        pitch = None
        roll = None

        for op, payload in operations:
            if op == "pitch":
                pitch = payload
            elif op == "roll":
                roll = payload
            elif op == "index":
                index_payload = payload
            elif op == "scatter":
                scatter_points = payload

        # Guard defaults
        index_payload = index_payload or {}
        scatter_points = scatter_points or []

        # Build uniforms using the index payload (which includes derived angles)
        uniforms = pack_index_to_uniforms(index_payload)

        # Pack scatter points into a vertex buffer
        vb = pack_scatter_to_vertex_buffer(scatter_points)

        # Store locally (prototype)
        self.uniforms = uniforms
        self.vertex_buffer = vb

        return {"uniforms": uniforms, "scatter_buffer": vb}

    # Optional: demonstrate how to upload to moderngl if available
    def upload_to_moderngl(self, ctx, prepared: Dict[str, Any]):
        """Given a moderngl context `ctx`, upload uniforms & buffers and return
        created objects. This is a best-effort helper and may fail cleanly if
        moderngl isn't available in the environment.
        """
        if np is None:
            raise RuntimeError("numpy required for upload_to_moderngl")

        uniforms = prepared["uniforms"]
        scatter_buf = prepared["scatter_buffer"]

        # Create vertex buffer (interleaved float32)
        vbo = ctx.buffer(scatter_buf.tobytes()) if hasattr(scatter_buf, "tobytes") else ctx.buffer(scatter_buf)

        # Example vertex array format: 2 floats (pos) + 1 float (channel)
        vao_content = [(vbo, "2f 1f", "in_pos", "in_channel")]

        # Minimal shader strings (vertex + fragment) to illustrate uniform usage.
        # Real shaders would expect proper locations/names and layout qualifiers.
        vertex_shader = """
        #version 330
        in vec2 in_pos;
        in float in_channel; // 0,1,2 -> r,g,b
        uniform float u_pitch_rad;
        uniform float u_roll_rad;
        uniform float u_scale_factor;
        void main() {
            // Apply simple rotation from pitch/roll to 2D position as an example
            float s = sin(u_pitch_rad);
            float c = cos(u_roll_rad);
            vec2 pos = in_pos * u_scale_factor;
            pos = vec2(pos.x * c - pos.y * s, pos.x * s + pos.y * c);
            gl_Position = vec4(pos * 2.0 - 1.0, 0.0, 1.0); // naive mapping
        }
        """

        fragment_shader = """
        #version 330
        out vec4 fragColor;
        uniform float u_r_mean;
        uniform float u_g_mean;
        uniform float u_b_mean;
        void main() {
            fragColor = vec4(u_r_mean, u_g_mean, u_b_mean, 1.0);
        }
        """

        prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        # Create VAO
        vao = ctx.vertex_array(prog, vao_content)

        # Set uniforms (moderngl accepts numpy scalars or python floats)
        for name, value in uniforms.items():
            if name in prog:
                prog[name].value = float(value)

        return {"vbo": vbo, "vao": vao, "program": prog}


# --- Example usage ---

def main():
    # Build a simple RGB image with distinct R/G/B regions
    rgb_matrix = [
        [[255, 10, 10], [255, 5, 5], [200, 20, 20]],
        [[10, 255, 10], [5, 255, 5], [20, 200, 20]],
        [[10, 10, 255], [5, 5, 255], [20, 20, 200]],
    ]

    # Use the built-in Prismatics wiring to produce operations
    backend = ExampleGPUBackend()

    # Use a local PrintBackend-like executor for demonstration: execute() should
    # accept operations, but we only need the operations data, so we compose
    # using Prismatics.wire_rgb and then inspect operations
    class CollectorBackend:
        def __init__(self):
            self.ops = None

        def execute(self, operations):
            # In a real backend this would perform GPU work. We just keep ops.
            self.ops = operations
            return {"status": "collected"}

    collector = CollectorBackend()
    p = Prismatics(collector)  # backend used only to capture ops on compute()
    p.wire_rgb(rgb_matrix, threshold=0.6)

    # At this point p.operations is populated; instead call compute() to run
    p.compute()

    ops = collector.ops
    print("Collected operations:")
    for op, payload in ops:
        print(f" - {op}:", type(payload), end="\n")

    prepared = backend.prepare_gpu_objects(ops)
    print("Prepared uniforms:")
    for k, v in prepared["uniforms"].items():
        print(f"  {k}: {v}")

    scatter_buf = prepared["scatter_buffer"]
    if np is not None and hasattr(scatter_buf, "shape"):
        print("Scatter buffer shape:", scatter_buf.shape)
        print(scatter_buf[: min(10, len(scatter_buf))])
    else:
        print("Scatter buffer length (bytes):", len(scatter_buf) if scatter_buf else 0)

    # Optional: attempt to upload to moderngl if available
    try:
        import moderngl

        # Create a simple standalone context (may fail in headless CI)
        ctx = moderngl.create_standalone_context()
        objects = backend.upload_to_moderngl(ctx, prepared)
        print("Uploaded to moderngl: ", objects.keys())
    except Exception as exc:  # pragma: no cover - optional runtime
        print("moderngl upload skipped (not available or failed):", exc)


if __name__ == "__main__":
    main()
