import json
import os
import pytest
from pydantic import ValidationError
from dotbimpy import File, Element, Mesh, Color, Rotation, Vector


TEST_FILES_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".local",
    "nottests",
    "unittests",
    "test_files",
)

GUID_A = "76e051c1-1bd7-44fc-8e2e-db2b64055068"
GUID_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _pyramid_mesh():
    return Mesh(
        mesh_id=0,
        coordinates=[
            0.0, 0.0, 0.0,
            10.0, 0.0, 0.0,
            10.0, 10.0, 0.0,
            0.0, 10.0, 0.0,
            5.0, 5.0, 4.0,
        ],
        indices=[
            0, 1, 2,
            0, 2, 3,
            0, 1, 4,
            1, 2, 4,
            2, 3, 4,
            3, 0, 4,
        ],
    )


def _pyramid_element():
    return Element(
        mesh_id=0,
        color=Color(r=255, g=255, b=0, a=255),
        guid=GUID_A,
        rotation=Rotation(qx=0, qy=0, qz=0, qw=1.0),
        vector=Vector(x=0, y=0, z=0),
        type="Structure",
        info={"Name": "Pyramid"},
    )


def _cube_mesh(mesh_id=0):
    return Mesh(
        mesh_id=mesh_id,
        coordinates=[
            0.0, 0.0, 0.0,
            10.0, 0.0, 0.0,
            10.0, 10.0, 0.0,
            0.0, 10.0, 0.0,
            0.0, 0.0, 10.0,
            10.0, 0.0, 10.0,
            10.0, 10.0, 10.0,
            0.0, 10.0, 10.0,
        ],
        indices=[
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            0, 1, 5, 0, 5, 4,
            2, 3, 7, 2, 7, 6,
            0, 3, 7, 0, 7, 4,
            1, 2, 6, 1, 6, 5,
        ],
    )


def _cube_element(mesh_id=0, guid=GUID_B):
    return Element(
        mesh_id=mesh_id,
        color=Color(r=255, g=0, b=0, a=255),
        guid=guid,
        rotation=Rotation(qx=0, qy=0, qz=0, qw=1.0),
        vector=Vector(x=0, y=0, z=0),
        type="Cube",
        info={"Name": "TestCube"},
    )


def _pyramid_file():
    return File(
        schema_version="1.0.0",
        meshes=[_pyramid_mesh()],
        elements=[_pyramid_element()],
        info={"Author": "John Doe", "Date": "28.09.1999"},
    )


def _cube_file():
    return File(
        schema_version="1.0.0",
        meshes=[_cube_mesh()],
        elements=[_cube_element()],
        info={"Author": "Jane Doe"},
    )


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
class TestFileInit:
    def test_basic_init(self):
        f = _pyramid_file()
        assert f.schema_version == "1.0.0"
        assert len(f.meshes) == 1
        assert len(f.elements) == 1
        assert f.info == {"Author": "John Doe", "Date": "28.09.1999"}

    def test_defaults(self):
        f = File()
        assert f.schema_version == "1.0.0"
        assert f.meshes == []
        assert f.elements == []
        assert f.info == {}


# ---------------------------------------------------------------------------
# Equality
# ---------------------------------------------------------------------------
class TestFileEquality:
    def test_equal_files(self):
        assert _pyramid_file() == _pyramid_file()

    def test_different_schema_version(self):
        a = _pyramid_file()
        b = _pyramid_file()
        b.schema_version = "1.1.0"
        assert a != b

    def test_different_meshes(self):
        a = _pyramid_file()
        b = _cube_file()
        assert a != b

    def test_different_info(self):
        a = _pyramid_file()
        b = _pyramid_file()
        b.info = {"Author": "Someone Else"}
        assert a != b

    def test_eq_with_non_file(self):
        assert _pyramid_file().__eq__(42) is False


# ---------------------------------------------------------------------------
# __add__
# ---------------------------------------------------------------------------
class TestFileAdd:
    def test_add_creates_new_file(self):
        a = _pyramid_file()
        b = _cube_file()
        result = a + b
        assert isinstance(result, File)
        assert len(result.meshes) == 2
        assert len(result.elements) == 2

    def test_add_remaps_mesh_ids(self):
        a = _pyramid_file()
        b = _cube_file()
        result = a + b
        ids = [m.mesh_id for m in result.meshes]
        assert ids[0] == 0
        assert ids[1] == 1
        assert result.elements[1].mesh_id == 1

    def test_add_does_not_mutate_originals(self):
        a = _pyramid_file()
        b = _cube_file()
        a_meshes_before = len(a.meshes)
        b_meshes_before = len(b.meshes)
        _ = a + b
        assert len(a.meshes) == a_meshes_before
        assert len(b.meshes) == b_meshes_before

    def test_add_preserves_schema_version(self):
        a = _pyramid_file()
        b = _cube_file()
        result = a + b
        assert result.schema_version == a.schema_version

    def test_add_with_non_file_returns_not_implemented(self):
        assert _pyramid_file().__add__(42) is NotImplemented


# ---------------------------------------------------------------------------
# Save / Read round-trip
# ---------------------------------------------------------------------------
class TestFileSaveRead:
    def test_save_read_round_trip(self, tmp_path):
        original = _pyramid_file()
        path = str(tmp_path / "test.bim")
        original.save(path)
        loaded = File.read(path)
        assert loaded == original

    def test_save_produces_valid_json(self, tmp_path):
        path = str(tmp_path / "test.bim")
        _pyramid_file().save(path)
        with open(path, "r") as f:
            data = json.load(f)
        assert "schema_version" in data
        assert "meshes" in data
        assert "elements" in data
        assert "info" in data

    def test_save_excludes_null_face_colors(self, tmp_path):
        path = str(tmp_path / "test.bim")
        _pyramid_file().save(path)
        with open(path, "r") as f:
            data = json.load(f)
        assert "face_colors" not in data["elements"][0]

    def test_save_invalid_extension(self):
        with pytest.raises(ValueError, match="\\.bim"):
            _pyramid_file().save("test.json")

    def test_read_invalid_extension(self):
        with pytest.raises(ValueError, match="\\.bim"):
            File.read("test.json")

    def test_read_real_pyramid_file(self):
        path = os.path.join(TEST_FILES_DIR, "Pyramid.bim")
        if not os.path.exists(path):
            pytest.skip("Test .bim files not available")
        f = File.read(path)
        assert f.schema_version == "1.0.0"
        assert len(f.meshes) == 1
        assert len(f.elements) == 1
        assert f.elements[0].type == "Structure"

    def test_read_real_cubes_file(self):
        path = os.path.join(TEST_FILES_DIR, "Cubes.bim")
        if not os.path.exists(path):
            pytest.skip("Test .bim files not available")
        f = File.read(path)
        assert len(f.elements) == 3
