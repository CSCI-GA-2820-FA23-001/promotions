Feature: The promotion service back-end
    As a Marketing Manager
    I need a RESTful promotion catalog service
    So that I can manage promotions for my store

Background:
    Given the following promotions
        | name                           | description                          | products_type | promotion_code     | require_code | start_date   | end_date     | is_active |
        | "First Time Shopper Discount"  | "Get 10% off your first purchase"    | "all_types"   | "first10%"         | true         |  2019-06-02  | 2023-08-28   | false     |
        | "Holiday Sale"                 | "Big discounts for the holidays"     | "electronics" | "holidy"           | true        |  2023-11-15  | 2023-12-25   | true      |
        | "Clearance Special"            | "Clearance items at great prices"    | "clothing"    | "clearance2023"    | true         |  2023-09-01  | 2023-12-31   | true      |
        | "Cyber Monday Sale"            | "Big discounts for the CyberMonday"  | "all_types"   | "cybermonday2023"  | true         |  2023-11-20  | 2023-11-30   | true      |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "First Time Shopper Discount" in the results
    And I should see "Holiday Sale" in the results
    And I should see "Clearance Special" in the results
    And I should see "Cyber Monday Sale" in the results
    And I should not see "Flash Sale" in the results

Scenario: Create a promotion
    When I visit the "Home Page"
    And I set the "id" to "5"
    And I set the "name" to "Black Friday Sale"
    And I set the "description" to "promotion for Black Friday"
    And I set the "products_type" to "all_types"
    And I set the "code" to "BLCKFRI"
    And I set the Start Date to "2023-11-15"
    And I set the End Date to "2023-11-30"
    And I press the "Create" button
    Then I should see the message "Success"    

Scenario: Activate a promotion
    When I visit the "Home Page"
    And I set the "id" to "6"
    And I set the "name" to "Christmas Sale"
    And I set the "description" to "promotion for Christmas"
    And I set the "products_type" to "all_types"
    And I set the "code" to "XMAS"
    And I set the Start Date to "2023-12-15"
    And I set the End Date to "2023-12-30"
    And I press the "Create" button
    Then I should see the message "Success"    
    When I copy the "id" field
    And I press the "Activate" button
    Then I should see the message "Success"    
    And I should see "True" in the "Is Active" dropdown

Scenario: Deactivate a promotion
    When I visit the "Home Page"
    And I set the "id" to "7"
    And I set the "name" to "NY Sale"
    And I set the "description" to "promotion for NY 2024"
    And I set the "products_type" to "all_types"
    And I set the "code" to "NY24"
    And I set the Start Date to "2023-12-15"
    And I set the End Date to "2024-01-15"
    And I press the "Create" button
    Then I should see the message "Success"    
    When I copy the "id" field
    And I press the "Deactivate" button
    Then I should see the message "Success"    
    And I should see "False" in the "Is Active" dropdown

Scenario: Clear
    When I visit the "Home Page"
    And I set the "id" to "8"
    And I set the "name" to "NY Sale2"
    And I set the "description" to "promotion for NY 2024"
    And I set the "products_type" to "all_types"
    And I set the "code" to "NY24"
    And I set the Start Date to "2023-12-15"
    And I set the End Date to "2024-01-15"
    And I press the "Create" button
    Then I should see the message "Success"    
    When I copy the "id" field
    And I press the "Clear" button
    Then the "name" field should be empty
    And the "products_type" field should be empty
    And the "id" field should be empty
    And the "code" field should be empty