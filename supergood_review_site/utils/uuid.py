from uuid import UUID


def is_uuid(value: str):
    try:
        UUID(value)
        return True
    except ValueError:
        return False
