from bravo_api.blueprints.bailiff import DomainUser


def test_expected_domain_parsing():
    user = DomainUser("foo@example.com")
    assert user.domain == "example.com"


def test_bad_domain_cases():
    bad_emails = ["bar-no-domain", "bar@", ""]
    for email in bad_emails:
        user = DomainUser(email)
        assert user.domain == ""


def test_authenticated():
    allowed_user = DomainUser(f"foo@{DomainUser.permitted_domain}")
    disallowed_user = DomainUser("foo@disallowed.example.com")

    print(disallowed_user)

    assert allowed_user.is_authenticated is True
    assert disallowed_user.is_authenticated is False


def test_permitted_domain():
    old_domain_permitted = DomainUser.permitted_domain
    new_domian_permitted = "new.example.com"

    user = DomainUser(f"bar@{new_domian_permitted}")
    assert user.is_authenticated is False

    DomainUser.set_permitted_domain(new_domian_permitted)
    assert user.is_authenticated is True

    DomainUser.permitted_domain = old_domain_permitted
