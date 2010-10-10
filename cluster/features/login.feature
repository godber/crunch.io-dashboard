Feature: Login

    Scenario: The root URL redirects to the login page
        Given I access the url "/"
        Then I am redirected to the url "/accounts/login/?next=/"

    Scenario: The root URL displays the Login Screen
        Given I access the url "/accounts/login/"
        Then I see the form "loginform"

    Scenario: The register URL displays the Register Message
        Given I access the url "/cluster/register/"
        Then I see the header "Register"

