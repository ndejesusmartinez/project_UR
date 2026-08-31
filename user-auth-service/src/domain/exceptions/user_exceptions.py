class UserAlreadyExistsException(Exception):
    """Lanzada cuando se intenta registrar un teléfono ya existente."""
    pass

class InvalidCredentialsException(Exception):
    """Lanzada cuando el inicio de sesión falla por credenciales o clave errónea."""
    pass

class UserNotFoundException(Exception):
    """Lanzada cuando el usuario no existe en la base de datos."""
    pass