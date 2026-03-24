import pytest
from uuid import UUID
from pydantic import ValidationError
from dotbimpy import Element, Color, Rotation, Vector


GUID_A = "76e051c1-1bd7-44fc-8e2e-db2b64055068"
GUID_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _make_element(**overrides):
    defaults = dict(
        mesh_id=0,
        color=Color(r=255, g=0, b=0, a=255),
        guid=GUID_A,
        rotation=Rotation(qx=0, qy=0, qz=0, qw=1.0),
        vector=Vector(x=0, y=0, z=0),
        type="Beam",
        info={"Name": "TestBeam"},
    )
    defaults.update(overrides)
    return Element(**defaults)


class TestElementInit:
    def test_basic_init(self):
        e = _make_element()
        assert e.mesh_id == 0
        assert e.color == Color(r=255, g=0, b=0, a=255)
        assert e.guid == UUID(GUID_A)
        assert e.type == "Beam"
        assert e.info == {"Name": "TestBeam"}
        assert e.face_colors is None

    def test_init_with_face_colors(self):
        fc = [255, 0, 0, 255, 0, 255, 0, 255]
        e = _make_element(face_colors=fc)
        assert e.face_colors == fc

    def test_guid_coerced_to_uuid(self):
        e = _make_element()
        assert isinstance(e.guid, UUID)

    def test_invalid_guid_rejected(self):
        with pytest.raises(ValidationError, match="guid"):
            _make_element(guid="not-a-uuid")

    def test_negative_mesh_id_rejected(self):
        with pytest.raises(ValidationError, match="mesh_id"):
            _make_element(mesh_id=-1)


class TestElementEquality:
    def test_equal_elements(self):
        assert _make_element() == _make_element()

    def test_different_mesh_id(self):
        assert _make_element(mesh_id=0) != _make_element(mesh_id=1)

    def test_different_color(self):
        assert _make_element(color=Color(r=255, g=0, b=0, a=255)) != _make_element(
            color=Color(r=0, g=255, b=0, a=255)
        )

    def test_different_guid(self):
        assert _make_element(guid=GUID_A) != _make_element(guid=GUID_B)

    def test_different_rotation(self):
        assert _make_element(rotation=Rotation(qx=0, qy=0, qz=0, qw=1.0)) != _make_element(
            rotation=Rotation(qx=1.0, qy=0, qz=0, qw=0)
        )

    def test_different_vector(self):
        assert _make_element(vector=Vector(x=0, y=0, z=0)) != _make_element(
            vector=Vector(x=1.0, y=0, z=0)
        )

    def test_different_type(self):
        assert _make_element(type="Beam") != _make_element(type="Column")

    def test_different_info(self):
        assert _make_element(info={"Name": "A"}) != _make_element(info={"Name": "B"})

    def test_different_face_colors(self):
        assert _make_element(face_colors=[255, 0, 0, 255]) != _make_element(
            face_colors=[0, 255, 0, 255]
        )

    def test_face_colors_none_vs_present(self):
        assert _make_element(face_colors=None) != _make_element(
            face_colors=[255, 0, 0, 255]
        )

    def test_eq_with_non_element(self):
        assert _make_element().__eq__(42) is False

    def test_equals_without_mesh_id(self):
        a = _make_element(mesh_id=0)
        b = _make_element(mesh_id=99)
        assert a.equals_without_mesh_id(b) is True

    def test_equals_without_mesh_id_different_type(self):
        a = _make_element(type="Beam")
        b = _make_element(type="Column")
        assert a.equals_without_mesh_id(b) is False

    def test_equals_without_mesh_id_non_element(self):
        assert _make_element().equals_without_mesh_id(42) is False


class TestElementFaceColors:
    def test_has_face_colors_true(self):
        e = _make_element(face_colors=[255, 0, 0, 255])
        assert e.check_if_has_face_colors() is True

    def test_has_face_colors_false(self):
        e = _make_element()
        assert e.check_if_has_face_colors() is False
