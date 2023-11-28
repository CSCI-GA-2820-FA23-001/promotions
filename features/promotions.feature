Feature: The promotion service back-end
    As a Marketing Manager
    I need a RESTful promotion catalog service
    So that I can manage promotions for my store

Background:
    Given the following promotions
        | name                           | description                          | products_type | promotion_code     | require_code | start_date   | end_date     | is_active |
        | "First Time Shopper Discount"  | "Get 10% off your first purchase"    | "all_types"   | "first10%"         | true         |  2019-06-02  | 2023-08-28   | false     |
        | "Holiday Sale"                 | "Big discounts for the holidays"     | "electronics" | "holidy"               | true        |  2023-11-15  | 2023-12-25   | true      |
        | "Clearance Special"            | "Clearance items at great prices"    | "clothing"    | "clearance2023"    | true         |  2023-09-01  | 2023-12-31   | true      |
        | "Cyber Monday Sale"            | "Big discounts for the CyberMonday"  | "all_types"   | "cybermonday2023"  | true         |  2023-11-20  | 2023-11-30   | true      |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion REST API Service"
    And I should not see "404 Not Found"
