from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role


def test_admin_implies_premium_and_freemium() -> None:
    user = AuthenticatedUser(user_id="u1", roles=[Role.ADMIN])

    assert user.has_role(Role.ADMIN)
    assert user.has_role(Role.PREMIUM)
    assert user.has_role(Role.FREEMIUM)


def test_premium_implies_freemium_but_not_admin() -> None:
    user = AuthenticatedUser(user_id="u2", roles=[Role.PREMIUM])

    assert not user.has_role(Role.ADMIN)
    assert user.has_role(Role.PREMIUM)
    assert user.has_role(Role.FREEMIUM)


def test_freemium_only_has_freemium() -> None:
    user = AuthenticatedUser(user_id="u3", roles=[Role.FREEMIUM])

    assert not user.has_role(Role.ADMIN)
    assert not user.has_role(Role.PREMIUM)
    assert user.has_role(Role.FREEMIUM)
