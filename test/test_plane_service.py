from controller.plane import plane_service


def test_plane_service():
    # Arrange
    # Actual
    actual = plane_service
    expected = plane_service
    # Assert
    assert actual == expected
