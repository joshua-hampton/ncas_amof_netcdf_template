def test_check_requirements():
    with open("pyproject.toml") as f:
        p_data = f.read()
    with open("requirements.txt") as f:
        r_data = f.read()
    pyproject_requirements = (
        "".join(p_data.split("dependencies")[1].split("[")[1].split("]")[0].split("\n"))
        .replace(" ", "")
        .replace('"', "")
        .split(",")
    )
    requirements_requirements = r_data.strip().replace(" ", "").split("\n")
    assert set(pyproject_requirements) == set(requirements_requirements)
