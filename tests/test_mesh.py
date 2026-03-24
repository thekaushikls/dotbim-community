import pytest
from pydantic import ValidationError
from dotbimpy import Mesh


class TestMeshValidation:
    def test_empty_mesh(self):
        m = Mesh()
        assert m.coordinates == []
        assert m.indices == []

    def test_one_vertex_no_faces(self):
        m = Mesh(mesh_id=0, coordinates=[1.0, 2.0, 3.0], indices=[])
        assert len(m.coordinates) == 3
        assert len(m.indices) == 0

    def test_valid_single_triangle(self):
        m = Mesh(
            mesh_id=0,
            coordinates=[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            indices=[0, 1, 2],
        )
        assert len(m.coordinates) == 9
        assert len(m.indices) == 3

    def test_coordinates_not_divisible_by_3(self):
        with pytest.raises(
            ValidationError, match="len\\(coordinates\\) must be divisible by 3"
        ):
            Mesh(mesh_id=0, coordinates=[1.0, 2.0], indices=[0])

    def test_indices_not_divisible_by_3(self):
        with pytest.raises(
            ValidationError, match="len\\(indices\\) must be divisible by 3"
        ):
            Mesh(mesh_id=0, coordinates=[1.0, 2.0, 3.0], indices=[0])

    def test_index_out_of_range(self):
        with pytest.raises(
            ValidationError, match="Index 2 out of range for 1 vertices"
        ):
            Mesh(mesh_id=0, coordinates=[1.0, 2.0, 3.0], indices=[0, 1, 2])

    def test_indices_with_empty_coordinates(self):
        with pytest.raises(
            ValidationError,
            match="Indices reference vertices but coordinates list is empty",
        ):
            Mesh(mesh_id=0, coordinates=[], indices=[0, 1, 2])
