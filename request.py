"""
- Beaux Blanchard
- Mission Control LLC
- Request Handler

=======
NOTES:

    - Phone numbers should be given in the following Regex pattern: ^\+?[\d\s\-.\/()]{8,20}$
    - The key "line_items" does not always have the same makeup from function to function and response to response. Make sure that you treat "line_items" properly.
    - Lulu supports all instances of "line_items" to be named "items". Whichever name you give will be the name you receive.
    - There a few functions with the lulu_ prefix. These functions have an alternate form without that prefix that uses a simple, universal dictionary
      in an attempt to make the developer's life easier. Details are below the remainder of the original documentation.

=======

make_sku_id(gloss): Returns a valid SKU string based on gloss, raises error otherwise
    gloss: (string) A string that is either "matte" or "glossy"

# This function sends a file to Lulu to determine if the file is in the correct format or not, or "validation".
# This function is specifically for validating files that will make up the interior of the book.
# This process is also run when a print-job is submitted, but you can validate files without submitting a print-job through this function.
# Lulu needs some amount of time (as short as a few seconds) to validate the file, so checking the status of the validation is a different function.
post_interior_file_validation(link, pod_package_id=""): Returns the JSON response from lulu about the validity of the file stored in link. Validation can take some time.
    link: (string) A public link to the file for Lulu to validate
    pod_package_id: (string) Not necessary, although Lulu says that it is required to "run extended validation".

    The JSON response contains:
    {
        id: (integer) (required) The internal id of that particular file
        source_url: (string) (required) The URL where the file came from
        page_count: (string) The detected page count of the file
        errors: (array of strings) Any detected errors in the file
        status: (string) "VALIDATING" (validation in progress), "VALIDATED" (validation successful), "ERROR" (something went wrong)
        valid_pod_package_ids: (array of strings) Any valid pod_package_ids for source file
    }

    OR
    {
        detail: (string) The error message
    }


# This function retrieves the current status of the interior file validation via an ID. You get this ID when you post a file validation.
get_interior_file_validation(id): Returns the JSON response from lulu about the validity of the file stored at id. Validation can take some time.
    id: (integer) The internal id of the file for Lulu to get validation information from.

    The JSON response is identical to post_file_validation()


# This function sends a file for the cover of a book to Lulu for validation, similar to the interior posting function.
# The response schema is slightly different for this function, as is the necessary parameters. Again, since Lulu needs
# time to validate files, you can retrieve the status of the validation in the following function.
post_cover_file_validation(link, pod_package_id, interior_page_count): Returns the JSON response from Lulu about the validity of the file stored at link. Validation can take some time.
    link: (string) (required) A public link to the cover file for Lulu to validate
    pod_package_id: (string) (required) A valid pod_package_id for the book that the cover will belong to.
    interior_page_count: (integer) (required) The number of pages for the book that the cover will belong to.

    The JSON response contains:
        id: (integer) (required) The internal id of the cover file, used to later get validation information from.
        source_url: (string) (required) The URL where the cover file came from
        errors: (array of strings) Any detected errors in the cover file
        status: (string) "NORMALIZING", "NORMALIZED", or "ERROR"

    OR
        detail: (string) The error message

    OR
        Something else. In the event you make a bad request, such as leaving out required attributes, the JSON file
        will contain some kind of error message that isn't simply a string. Based on examples, simply printing the
        entire JSON file will make evident what went wrong.

# This function retrieves the status of a cover file validation process via an ID. You get the ID when you post the cover file to validate.
get_cover_file_validation(id): Returns the JSON response from Lulu about the validity of the cover file stored at a given id. Validation can take some time.
    id: (integer) (required) The id that Lulu stores the cover file

    The JSON response is identical to post_cover_file_validation()


# This function uses their online cost calculator to give an estimated cost of a print-job, including a breakdown of
# shipping costs, discounts, taxes, and more.
calculate_print_job_cost(line_items, shipping_address, shipping_option): Returns a JSON response from Lulu about the costs of a single print-job.
    line_items: (list of dictionaries) (required) A list of dictionaries containing information about each individual book.
        Format of each dictionary (all entries required):
        {
            "page_count": (integer) The number of pages
            "pod_package_id": (string) The SKU id for that book
            "quantity": (integer32) The number of that book to print
        }
    shipping_address: (dictionary) (required) A dictionary containing the shipping information for the book.
        Format of dictionary (give as many things as you know, but not all entries are required. Required entries are marked with a *):
        {
        *   city: (string) (required) The city to ship to
        *   country_code: (string) (required) A two-letter country code adhering to ISO 3166-2 standard (https://en.wikipedia.org/wiki/ISO_3166-2)
            email: (string) The email address that all shipping questions should be sent to. This is NOT the customer, it is you, the developer/business owner.
            is_business: (boolean, defaulted to False) Unless you are shipping to a business, do not include this flag. Some shipping carriers do not deliver to businesses on some days, making this flag sometimes important.
        *   name: (string) (semi-required) The first and last name of the person. Not required, but at least one of name or organization is required.
        *   organization: (string) (semi-required) The name of the organization to deliver to. Not required, but at least one of name or organization is required.
        *   phone_number: (string <= 20 characters) (required) The phone number of the person to deliver to. Lulu does not use this, but it is required by their mail carriers. If this is not here, they will not deliver it. Must match Validation Regex Pattern: ^\+?[\d\s\-.\/()]{8,20}$
        *   postcode: (string <= 64 characters) (required) The postal code
        *   state_code: (string of 2 or 3 characters) (semi-required) The 2 or 3 letter state codes (ISO-3166-2 subdivision codes) that are required for some countries, such as the US, Canada, Mexico...
        *   street1: (string) (required) The first address line
            street2: (string) The second address line
            title: (string, one of "MR", "MISS", "MRS", "MS", or "DR") The title of the person
        }
    shipping_option: (string, one of "MAIL", "PRIORITY_MAIL", "GROUND_HD", "GROUND_BUS", "GROUND", "EXPEDITED", "EXPRESS") (required) The shipping option to use.

    The JSON response contains:
    {
        shipping_address: (dictionary) The shipping information for the book
            This dictionary is identical to shipping_address in calculate_print_job_cost()
        currency: (string) (required) The currency for the costs
        line_item_costs: (array of dictionaries) (required) A list of dictionaries containing cost information for each book.
            Each dictionary contains (all items required except for unit_tier_cost):
            {
                cost_excl_discounts: (string) Per unit cost without any discounts applied.
                discounts: (array of dictionaries) A list of the discounts applied for each item, if applicable. Each dictionary contains an "amount" (string) and a "description" (string)
                quantity: (integer) The number of items being printed that all calculations are based on
                tax_rate: (string) The applied tax rate
                total_cost_excl_discounts: (string) The total cost of the order without discounts applied
                total_cost_excl_tax: (string) The total cost of the order without taxes applied
                total_cost_incl_tax: (string) The total cost of the order with taxes applied
                total_tax: (string) The total tax applied
                unit_tier_cost: (string) Per unit cost with tier discount applied. Not applicable for non-tier (list-price) customers.
            }
        shipping cost: (dictionary) (required) Summary of the combined shipping and handling costs.
            The dictionary contains (none of the entries are required):
            {
                tax_rate: (string) The tax rate applied on shipping and handling
                total_cost_excl_tax: (string) The total cost of the order without taxes applied
                total_cost_incl_tax: (string) The total cost of the order with taxes applied
                total_tax: (string) The total tax applied
            }
        fulfillment_cost: (dictionary) Summary of the fulfillment fee costs.
            This dictionary is identical to the dictionary in shipping costs
        total_cost_excl_tax: (string) (required) The total cost of the order without taxes applied
        total_cost_incl_tax: (string) (required) The total cost of the order with taxes applied
        total_discount_amount: (string) (required) The total discount applied
        total_tax: (string) (required) The total tax applied
        fees: (list of dictionaries) A summary of the fees applied, if applicable
            Each dictionary contains (none of the entries are required):
            {
                currency: (string) The currency for the costs
                fee_type: (string) The type of fee being applied
                sku: (string) The SKU for the fee
                tax_rate: (string) The tax rate applied to the fee
                total_cost_excl_tax: (string) The total cost of the fee without taxes applied
                total_cost_incl_tax: (string) The total cost of the fee with taxes applied
                total_tax: (string) The total tax applied to the fee
            }
    }
    OR
        detail: (string) The error message

    OR
        Something else. In the event you make a bad request, such as leaving out required attributes, the JSON file
        will contain some kind of error message that isn't simply a string. Based on examples, simply printing the
        entire JSON file will make evident what went wrong.


# This function searches through and returns all of your print-jobs. You can narrow down the search by the criteria given in filters.
lulu_get_print_jobs(filters): Returns a JSON response from Lulu about all print-jobs, based on the filter criteria given
    filters: (dictionary) A dictionary containing any search filters you would like to use on the response file.
        Format of dictionary (none of the parameters are required, passing nothing into this function will return all print-jobs)
        {
            page: (integer) The result page
            page_size: (integer) The number of results on a page
            created_after: (ISO 8601 timestamp) All print-jobs created after a given timestamp
            created_before: (ISO 8601 timestamp) All print-jobs created before a given timestamp
            modified_after: (ISO 8601 timestamp) All print-jobs modified after a given timestamp
            modified_before: (ISO 8601 timestamp) All print-jobs modified before a given timestamp
            status: (string) All print-jobs currently in a given status
            id: (string) Filter by id
            order_id: (string) Filter by order_id
            exclude_line_items: (boolean) Leave the line_items list out of the JSON response
            search: (string) Search across the fields id, external_id, order_id, status, line_item_id, line_item_external_id, line_item_title, line_item_tracking_id and shipping_address. (Will return any print-job where the item put into this field appears in any of the listed fields)
            ordering: (string) Which field to use when ordering the results. (e.g. putting date_created will order the results by date created)
        }

    The JSON response contains (all required):
    {
        count: (integer) The page number
        next: (string) A link
        previous: (string) A link
        results: (list of dictionaries) The results of the search
            Each dictionary contains:
            {
                contact_email: (string) (required) The contact email if shipping questions arise. This should not be the person you are shipping to, rather it should be you, the distributor/developer.
                costs: (dictionary) The cost summary of the print-job.
                    This dictionary contains:
                    {
                        currency: (string) (required) The currency for the costs
                        line_item_costs: (array of dictionaries) (required) A list of dictionaries containing cost information for each book.
                            Each dictionary contains (all items required except for unit_tier_cost):
                            {
                                cost_excl_discounts: (string) Per unit cost without any discounts applied.
                                discounts: (array of dictionaries) A list of the discounts applied for each item, if applicable. Each dictionary contains an "amount" (string) and a "description" (string)
                                quantity: (integer) The number of items being printed that all calculations are based on
                                tax_rate: (string) The applied tax rate
                                total_cost_excl_discounts: (string) The total cost of the order without discounts applied
                                total_cost_excl_tax: (string) The total cost of the order without taxes applied
                                total_cost_incl_tax: (string) The total cost of the order with taxes applied
                                total_tax: (string) The total tax applied
                                unit_tier_cost: (string) Per unit cost with tier discount applied. Not applicable for non-tier (list-price) customers.
                            }
                        shipping cost: (dictionary) (required) Summary of the combined shipping and handling costs.
                            The dictionary contains (none of the entries are required):
                            {
                                tax_rate: (string) The tax rate applied on shipping and handling
                                total_cost_excl_tax: (string) The total cost of the order without taxes applied
                                total_cost_incl_tax: (string) The total cost of the order with taxes applied
                                total_tax: (string) The total tax applied
                            }
                        fulfillment_cost: (dictionary) Summary of the fulfillment fee costs.
                            This dictionary is identical to the dictionary in shipping costs
                        total_cost_excl_tax: (string) (required) The total cost of the order without taxes applied
                        total_cost_incl_tax: (string) (required) The total cost of the order with taxes applied
                        total_discount_amount: (string) (required) The total discount applied
                        total_tax: (string) (required) The total tax applied
                    }
                estimated_shipping_dates: (dictionary) The estimated shipping and delivery dates for the print-job
                    This dictionary contains (all in ISO 8601 format):
                    {
                        arrival_max: (string) The slowest estimated delivery date
                        arrival_min: (string) The fasted estimated delivery date
                        dispatch_max: (string) The slowest estimated ship date
                        dispatch_min: (string) The fasted estimated ship date
                    }
                external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
                id: (integer) (required) Lulu's identifier for the print-job
                line_items: (list of dictionaries) (required) The line items for a print-job. ***This field can also be labeled as "items"***
                    Each dictionary contains:
                    {
                        external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
                        id: (integer) (required) Lulu's identifier for the print-job
                        page_count: (integer) The page count of the printable
                        pod_package_id: (string <= 27 characters) The SKU of the printable
                        printable_id: (string uuid) The id of the printable
                        printable_normalization: (dictionary) Shows the normalization process of the printable. This contains the cover and interior files for the printable.
                            This dictionary contains two identical and required items:
                            {
                                cover: (dictionary) The normalization of the cover source file
                                    This dictionary contains:
                                    {
                                        job_id: (integer) The id of the normalization job
                                        normalized_file: (dictionary) The resulting normalized file
                                            This dictionary contains:
                                            {
                                                file_id: (integer) The file id.
                                                filename: (string) The name of the file
                                            }
                                        source_md5_sum: (string) The md5 hash of the source file, checking its integrity
                                        source_url: (string) (required) The url of the source file
                                    }
                                interior: (dictionary) The normalization of the interior source file
                                    This dictionary is identical to the "cover" dictionary
                            }
                        quantity: (integer) (required) Quantity of printed books for this line item
                        status: (dictionary) (required) The status of the line item, containing the item processing status along with additional information
                            This dictionary contains (all items required):
                            {
                                messages: (dictionary) A map of all additional information about the status. The default for this item is blank
                                    This dictionary contains (all items optional):
                                    {
                                        delay: (string <= 64 characters) Expected delay in hours due to error status
                                        error: (string) The general error message
                                        info: (string) General information about the status
                                        printable_normalization: (dictionary) A map of printable normalization messages/data
                                            This dictionary contains two identical and non-required items:
                                            {
                                                cover: (list of strings) A list of strings conveying normalization information/data about the cover file
                                                interior: (list of strings) A list of strings conveying normalization information/data about the interior file
                                            }
                                        timestamp: (string ISO 8601 timestamp) A timestamp of the last status change
                                        tracking_urls: (string OR list of strings) All of the tracking urls
                                        tracking_id: (string) The tracking id of this line item
                                        carrier_name: (string) The name of the carrier handling the shipment
                                    }
                                name: (string) (required) The actual processing status of the print-job, defaulted to "CREATED"
                                    This string is always one of the following: "CREATED", "ACCEPTED", "REJECTED", "IN_PRODUCTION", "ERROR", "SHIPPED"
                            }
                        title: (string <= 255 characters) The title of the line-item, and should be what appears on the cover of the book
                        tracking_urls: (list of strings) The tracking urls for this line-item's shipment
                        carrier_name: (string) The name of the carrier handling the shipment
                    }
                order_id: (string) The reference to this order, created when the order is created
                production_delay: (integer between 60 (default) and 2880) The number of minutes that the order is delayed prior to being sent to production. Lulu creates an artificial delay prior to beginning production so that orders can be canceled. After being sent to production, orders can no longer be canceled.
                production_due_time: (string, ISO 8601 timestamp) The target timestamp for when this item will move into production
                shipping_address: (dictionary) (required) The shipping address of the customer.
                    This dictionary is identical to shipping_address in calculate_print_job_cost(), but with two additional fields:
                    {
                        warnings: (list of dictionaries) Any warnings found during address validation
                            Each dictionary contains (no items required):
                            {
                                type: (string) The type of warning
                                code: (string) A warning code that describes what was suggested by validation
                                path: (string) Describes the validation origin of the warning
                                message: (string) The warning message that includes the suggested change
                            }
                        suggested_address: (dictionary) The address that was suggested by validation
                            This dictionary contains (no items required):
                            {
                                country_code: (string) The country code that was suggested by validation
                                state_code: (string) The state code that was suggested by validation
                                postcode: (string) The postcode that was suggested by validation
                                city: (string) The city that was suggested by validation
                                street1: (string) The 1st street line that was suggested by validation
                                street2: (string) The 2nd street line that was suggested by validation
                            }
                    }
                shipping_level: (string) (required) The shipping level that the print-job is being shipped with
                    This string is one of: "MAIL" "PRIORITY_MAIL" "GROUND_HD" "GROUND_BUS" "GROUND" "EXPEDITED" "EXPRESS"
                tax_country: (string <= 2 characters) ISO 3166-1 alpha-2 country code of the tax country determined for this job
            }
    }

    OR
    {
        detail: (string) (required) The error message
    }


# Use this function to send a print-job for Lulu to execute.
lulu_create_print_job(line_items, shipping_address, shipping_level, contact_email, external_id, production_delay): Sends a print-job for Lulu to execute. When you create a print-job, it will remain in the "UNPAID" state until manually paid for on the developer website. Alternatively, you can attach a credit card on file, which will be charged automatically and move the print-job to the next phase.
    line_items: (list of dictionaries) (required) The list of items that you want to have printed.
        Each dictionary contains:
            To tell Lulu what you want to print, there are three different options:
                {
                    cover: (string OR dictionary) (required) The cover file to print
                        If (string): provide the url of the cover file
                        If (dictionary):
                            {
                                source_md5_sum: (string) An md5 hash of the source file to check integrity
                                source_url: (string) (required) The url of the source file

                            }
                    interior: (string OR dictionary) (required) The interior file to print
                        The makeup of this entry is identical to the cover entry
                }
            OR
                {
                    printable_normalization: (dictionary) Represents the normalization process of the source files.
                        This dictionary contains:
                        {
                            cover: (dictionary) (required) The normalization of the cover file
                                This dictionary contains:
                                    {
                                        job_id: (integer) The id of the normalization job
                                        source_md5_sum: (string) An md5 hash of the source file to check integrity
                                        source_url: (string) (required) The url of the source file
                                    }
                            interior: (dictionary) (required) The normalization of the interior file
                                The makeup of this dictionary is identical to the cover dictionary
                        }
                }
            OR
                printable_id: (string uuid) Especially useful for reprints, if the printable already has an ID, then you can simply give this ID in order to direct Lulu to the files you want to have printed.

            Regardless of the method of delivery for the content files, the rest of the entries for line_items are as follows:
            {
                external_id: (string) An arbitrary ID that you can set to help you identify files within your own system. Lulu does not use this string, and it is not required. They will however, return this external ID whenever you request the print-job.
                pod_package_id: (string <= 27 characters) The SKU of this item (how you want it printed)
                quantity: (integer) (required) How many of this item to print
                title: (string <= 255 characters) (required) The title of the line-item (should be what is on the cover)
            }

    shipping_address: (dictionary) (required) The shipping address of the customer, along with some other information.
        This dictionary is identical to the shipping_address dictionary in calculate_print_job_cost(), but with one additional field:
        {
            recipient_tax_id: (string) (required for deliveries in Brazil, Chile, and Mexico) The recipients tax identification number
        }
    shipping_level: (string) (required) The shipping level that you want to use for the print-job
        Must be one of: "MAIL" "PRIORITY_MAIL" "GROUND_HD" "GROUND_BUS" "GROUND" "EXPEDITED" "EXPRESS"
    contact_email: (string) (required) The contact email that you want to use for the print-job. This is Lulu uses to ask questions if there is something they need to ask about the print-job. This should not be the end-customer email, but instead you, the developer/distributor placing the print-job order.
    external_id: (string) An arbitrary string that the developer can use to help identify print-jobs on their end. Lulu does not use this ID, but will store and return this ID with it's associated print-job.
    production_delay: (integer between 60 and 2880) Lulu places an artificial delay between being sent the order and beginning the printing process, in the event of delays. It is automatically set to 60 (1 hour), but can be set from anywhere between 60 (1 hour) and 2880 (48 hours).

    The JSON response contains:
    {
        contact_email: Identical to the contact email provided
        costs: (dictionary) A summary of the costs of a print-job
            This dictionary contains:
            {
                line_item_costs: (dictionary) A dictionary containing cost information for the print-job.
                    This dictionary contains:
                    {
                        cost_excl_discounts: (string) Per unit cost without any discounts applied.
                        discounts: (array of dictionaries) A list of the discounts applied for each item, if applicable. Each dictionary contains an "amount" (string) and a "description" (string)
                        quantity: (integer) The number of items being printed that all calculations are based on
                        tax_rate: (string) The applied tax rate
                        total_cost_excl_discounts: (string) The total cost of the order without discounts applied
                        total_cost_excl_tax: (string) The total cost of the order without taxes applied
                        total_cost_incl_tax: (string) The total cost of the order with taxes applied
                        total_tax: (string) The total tax applied
                        unit_tier_cost: (string) Per unit cost with tier discount applied. Not applicable for non-tier (list-price) customers.
                    }
                shipping_cost: (dictionary) A summary of the shipping costs
                    This dictionary contains:
                    {
                        tax_rate: (string) The applied tax rate
                        total_cost_excl_tax: (string) The total cost of shipping without tax
                        total_cost_incl_tax: (string) The total cost of shipping with taxes applied
                        total_tax: (string) The total tax applied on shipping
                    }
                total_cost_excl_tax: (string) The total cost of the order without taxes applied
                total_cost_incl_tax: (string) The total cost of the order with taxes applied
                total_tax: (string) The total tax applied on the order
            }
        estimated_shipping_dates: (dictionary) The estimated shipping and delivery dates of a print-job
            This dictionary contains (all in ISO 8601 format):
                {
                    arrival_max: (string) The slowest estimated delivery date
                    arrival_min: (string) The fasted estimated delivery date
                    dispatch_max: (string) The slowest estimated ship date
                    dispatch_min: (string) The fasted estimated ship date
                }
        external_id: Identical to the provided external ID
        id: (integer) (required) The ID that Lulu uses to identify the print-job
        line_items: (list of dictionaries) (required) The line items of a print-job.
            Each dictionary contains:
            {
                external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
                id: (integer) (required) Lulu's identifier for the print-job
                page_count: (integer) The page count of the printable
                pod_package_id: (string <= 27 characters) The SKU of the printable
                printable_id: (string uuid) The id of the printable
                printable_normalization: (dictionary) Shows the normalization process of the printable. This contains the cover and interior files for the printable.
                    This dictionary contains two identical and required items:
                    {
                        cover: (dictionary) The normalization of the cover source file
                            This dictionary contains:
                            {
                                job_id: (integer) The id of the normalization job
                                normalized_file: (dictionary) The resulting normalized file
                                    This dictionary contains:
                                    {
                                        file_id: (integer) The file id.
                                        filename: (string) The name of the file
                                    }
                                source_md5_sum: (string) The md5 hash of the source file, checking its integrity
                                source_url: (string) (required) The url of the source file
                            }
                        interior: (dictionary) The normalization of the interior source file
                            This dictionary is identical to the "cover" dictionary
                    }
                quantity: (integer) (required) Quantity of printed books for this line item
                status: (dictionary) (required) The status of the line item, containing the item processing status along with additional information
                    This dictionary contains (all items required):
                    {
                        messages: (dictionary) A map of all additional information about the status. The default for this item is blank
                            This dictionary contains (all items optional):
                            {
                                delay: (string <= 64 characters) Expected delay in hours due to error status
                                error: (string) The general error message
                                info: (string) General information about the status
                                printable_normalization: (dictionary) A map of printable normalization messages/data
                                    This dictionary contains two identical and non-required items:
                                    {
                                        cover: (list of strings) A list of strings conveying normalization information/data about the cover file
                                        interior: (list of strings) A list of strings conveying normalization information/data about the interior file
                                    }
                                url: (string or list of strings) The tracking url(s)
                            }
                        name: (string) (required) The actual processing status of the print-job, defaulted to "CREATED"
                            This string is always one of the following: "CREATED", "ACCEPTED", "REJECTED", "IN_PRODUCTION", "ERROR", "SHIPPED"
                    }
                title: (string <= 255 characters) The title of the line-item, and should be what appears on the cover of the book
                tracking_id: (string) The tracking ID for this item
                tracking_urls: (list of strings) The tracking urls for this line-item's shipment
            }
        order_id: (string) The order ID that Lulu creates upon receiving a print-job
        production_delay: Identical to the production delay provided
        production_due_time: (string ISO 8601) The projected time for when this print-job will move into production
        shipping_address: (dictionary) Identical to the shipping address provided, with two additional components:
            {
                warnings: (list of dictionaries) Any warnings found during address validation
                    Each dictionary contains (no items required):
                    {
                        type: (string) The type of warning
                        code: (string) A warning code that describes what was suggested by validation
                        path: (string) Describes the validation origin of the warning
                        message: (string) The warning message that includes the suggested change
                    }
                suggested_address: (dictionary) The address that was suggested by validation
                    This dictionary contains (no items required):
                    {
                        country_code: (string) The country code that was suggested by validation
                        state_code: (string) The state code that was suggested by validation
                        postcode: (string) The postcode that was suggested by validation
                        city: (string) The city that was suggested by validation
                        street1: (string) The 1st street line that was suggested by validation
                        street2: (string) The 2nd street line that was suggested by validation
                    }
            }
        shipping_level: Identical to the provided shipping level
        tax_country: (string <= 2 characters) ISO 3166-1 alpha-2 country code of the tax country determined for this job
    }

    OR
        detail: (string) The error message

    OR
        Something else. In the event you make a bad request, such as leaving out required attributes, the JSON file
        will contain some kind of error message that isn't simply a string. Based on examples, simply printing the
        entire JSON file will make evident what went wrong.


# This function is similar to get_print_jobs, but instead of returning the actual print-job objects, it returns the number
# of print-jobs that meet the filters given. The only change in the parameters is that the "status" parameter in "filters" is required.
get_print_job_statistics(filters): Get the number of print-jobs that fall under a certain status, along with meeting any other listed criteria. This function is identical in nearly all aspects except for the return value to get_print_jobs()
    filters: Identical to get_print_jobs, but "status" must be filled

    The JSON response contains:
    {
        count: (integer) The number of print-jobs that meet the given filters
        status: (string) The status of the category of print-jobs
            Defaults to "CREATED", must be one of "CREATED" "REJECTED" "UNPAID" "PAYMENT_IN_PROGRESS" "PRODUCTION_READY" "PRODUCTION_DELAYED" "IN_PRODUCTION" "ERROR" "SHIPPED" "CANCELED"
    }
    OR
    {
        detail: (string) The error message
    }


# This function gives a singular print-job object that corresponds to a given ID.
lulu_get_single_print_job(id): Retrieve the information about a singular print-job based on id number
    id: (string) The print-job id

    The JSON response is very similar to an individual response in get_print_jobs(), with several additional fields, and several removed, as follows:
    {
        child_job_ids: (list of integers) The ids of any reprints of this print-job
        parent_job_id: (integer) If this item is a reprint, the original print-job id will be listed here.
        date_created: (string) The date the item was created
        date_modified: (string) The date the item was modified
        contact_email: (string) (required) The contact email if shipping questions arise. This should not be the person you are shipping to, rather it should be you, the distributor/developer.
        costs: (dictionary) The cost summary of the print-job.
            This dictionary contains:
            {
                currency: (string) (required) The currency for the costs
                line_item_costs: (array of dictionaries) (required) A list of dictionaries containing cost information for each book.
                    Each dictionary contains (all items required except for unit_tier_cost):
                    {
                        cost_excl_discounts: (string) Per unit cost without any discounts applied.
                        discounts: (array of dictionaries) A list of the discounts applied for each item, if applicable. Each dictionary contains an "amount" (string) and a "description" (string)
                        quantity: (integer) The number of items being printed that all calculations are based on
                        tax_rate: (string) The applied tax rate
                        total_cost_excl_discounts: (string) The total cost of the order without discounts applied
                        total_cost_excl_tax: (string) The total cost of the order without taxes applied
                        total_cost_incl_tax: (string) The total cost of the order with taxes applied
                        total_tax: (string) The total tax applied
                        unit_tier_cost: (string) Per unit cost with tier discount applied. Not applicable for non-tier (list-price) customers.
                    }
                shipping cost: (dictionary) (required) Summary of the combined shipping and handling costs.
                    The dictionary contains (none of the entries are required):
                    {
                        tax_rate: (string) The tax rate applied on shipping and handling
                        total_cost_excl_tax: (string) The total cost of the order without taxes applied
                        total_cost_incl_tax: (string) The total cost of the order with taxes applied
                        total_tax: (string) The total tax applied
                    }
                fulfillment_cost: (dictionary) Summary of the fulfillment fee costs.
                    This dictionary is identical to the dictionary in shipping costs
                total_cost_excl_tax: (string) (required) The total cost of the order without taxes applied
                total_cost_incl_tax: (string) (required) The total cost of the order with taxes applied
                total_discount_amount: (string) (required) The total discount applied
                total_tax: (string) (required) The total tax applied
            }
        estimated_shipping_dates: (dictionary) The estimated shipping and delivery dates for the print-job
            This dictionary contains (all in ISO 8601 format):
            {
                arrival_max: (string) The slowest estimated delivery date
                arrival_min: (string) The fasted estimated delivery date
                dispatch_max: (string) The slowest estimated ship date
                dispatch_min: (string) The fasted estimated ship date
            }
        external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
        id: (integer) (required) Lulu's identifier for the print-job
        line_items: (list of dictionaries) (required) The line items for a print-job. ***This field can also be labeled as "items"***
            Each dictionary contains:
            {
                reprint: (dictionary) A dictionary containing information about any reprints, if available
                    This dictionary contains:
                    {
                        defect: (string) The classification of defect
                        description: (string) The description of the defect
                        # There is no documentation for the following two entries, and I only know they exist through example code. I assume they are internal, and not useful on the developer side.
                        cost_center: (string?) No documentation provided
                        printer_at_fault: (string?) No documentation provided
                    }
                external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
                id: (integer) (required) Lulu's identifier for the print-job
                printable_id: (string uuid) The id of the printable
                printable_normalization: (dictionary) Shows the normalization process of the printable. This contains the cover and interior files for the printable.
                    This dictionary contains two identical and required items:
                    {
                        cover: (dictionary) The normalization of the cover source file
                            This dictionary contains:
                            {
                                job_id: (integer) The id of the normalization job
                                normalized_file: (dictionary) The resulting normalized file
                                    This dictionary contains:
                                    {
                                        file_id: (integer) The file id.
                                        filename: (string) The name of the file
                                    }
                                source_md5_sum: (string) The md5 hash of the source file, checking its integrity
                                source_url: (string) (required) The url of the source file
                            }
                        interior: (dictionary) The normalization of the interior source file
                            This dictionary is identical to the "cover" dictionary
                    }
                quantity: (integer) (required) Quantity of printed books for this line item
                status: (dictionary) (required) The status of the line item, containing the item processing status along with additional information
                    This dictionary contains (all items required):
                    {
                        messages: (dictionary) A map of all additional information about the status. The default for this item is blank
                            This dictionary contains (all items optional):
                            {
                                delay: (string <= 64 characters) Expected delay in hours due to error status
                                error: (string) The general error message
                                info: (string) General information about the status
                                printable_normalization: (dictionary) A map of printable normalization messages/data
                                    This dictionary contains two identical and non-required items:
                                    {
                                        cover: (list of strings) A list of strings conveying normalization information/data about the cover file
                                        interior: (list of strings) A list of strings conveying normalization information/data about the interior file
                                    }
                                timestamp: (string ISO 8601 timestamp) A timestamp of the last status change
                                tracking_urls: (string OR list of strings) All of the tracking urls
                                tracking_id: (string) The tracking id of this line item
                                carrier_name: (string) The name of the carrier handling the shipment
                            }
                        name: (string) (required) The actual processing status of the print-job, defaulted to "CREATED"
                            This string is always one of the following: "CREATED", "ACCEPTED", "REJECTED", "IN_PRODUCTION", "ERROR", "SHIPPED"
                    }
                title: (string <= 255 characters) The title of the line-item, and should be what appears on the cover of the book
            }
        order_id: (string) The reference to this order, created when the order is created
        production_delay: (integer between 60 (default) and 2880) The number of minutes that the order is delayed prior to being sent to production. Lulu creates an artificial delay prior to beginning production so that orders can be canceled. After being sent to production, orders can no longer be canceled.
        production_due_time: (string, ISO 8601 timestamp) The target timestamp for when this item will move into production
        shipping_address: (dictionary) (required) The shipping address of the customer.
            This dictionary is identical to shipping_address in calculate_print_job_cost(), but with two additional fields:
            {
                warnings: (list of dictionaries) Any warnings found during address validation
                    Each dictionary contains (no items required):
                    {
                        type: (string) The type of warning
                        code: (string) A warning code that describes what was suggested by validation
                        path: (string) Describes the validation origin of the warning
                        message: (string) The warning message that includes the suggested change
                    }
                suggested_address: (dictionary) The address that was suggested by validation
                    This dictionary contains (no items required):
                    {
                        country_code: (string) The country code that was suggested by validation
                        state_code: (string) The state code that was suggested by validation
                        postcode: (string) The postcode that was suggested by validation
                        city: (string) The city that was suggested by validation
                        street1: (string) The 1st street line that was suggested by validation
                        street2: (string) The 2nd street line that was suggested by validation
                    }
            }
        shipping_level: (string) (required) The shipping level that the print-job is being shipped with
            This string is one of: "MAIL" "PRIORITY_MAIL" "GROUND_HD" "GROUND_BUS" "GROUND" "EXPEDITED" "EXPRESS"
        tax_country: (string <= 2 characters) ISO 3166-1 alpha-2 country code of the tax country determined for this job
    }

    OR
    {
        detail: (string) (required) Details about the error message
    }


# This function gets the "cost" field of a print-job and returns it. You could simply use get_print_job() and retrieve the
# cost information from there, but I believe this option is given by Lulu so that the size of the package being sent is smaller.
get_print_job_costs(id): Return only the "cost" dictionary of a single print-job
    id: (string) (required) The id of the print-job to retrieve the cost from

    The JSON response is identical to the "cost" field of the response in get_single_print_job()

    OR
    {
        detail: (string) (required) Details about the error message
    }


# Similarly to get_print_job_costs, this function only returns the "status" of a print-job corresponding to an ID.
get_print_job_status(id): Return status information about a single print-job
    id: (string) (required) The id of the print-job to retrieve the status information from

    The JSON response contains:
    {
        changed: (string ISO 8601) (required) Timestamp of the latest status change
        message: (string) A status related message
        name: (string) The current status of the print-job
            Default: "CREATED", must be one of "CREATED" "REJECTED" "UNPAID" "PAYMENT_IN_PROGRESS" "PRODUCTION_READY" "PRODUCTION_DELAYED" "IN_PRODUCTION" "ERROR" "SHIPPED" "CANCELED"
    }

    OR
    {
        detail: (string) (required) Details about the error message
    }


# This function cancels a print-job, if possible. If a print-job has already been sent to the printers, you cannot cancel it.
# This is the reason that Lulu requires an artificial delay between receiving a print-job and sending it to the printers.
cancel_print_job(id): Cancel a print-job
    id: (string) (required) The id of the print-job to cancel

    The JSON response is identical to the response of get_print_job_status()

    OR
    Some other other error message of variable format. Printing out the JSON response should make the error clear.


# This function gives all of the possible shipping options for a given address. You could use this to give a customer
# options about which shipping option they would like to use for delivery.
retrieve_shipping_options(line_items, shipping_address, currency): Get the possible shipping options of a print-job
    line_items: (list of dictionaries) (required) A list of the items that would be shipped
        Each dictionary contains (all items required):
        {
            page_count: (integer) The page count of the book
            pod_package_id: (string) The pod package id (SKU) of the book
            quantity: (integer) The quantity of the book
        }
    shipping_address: (dictionary) (required) The shipping address of the book
        This dictionary contains:
        {
            country: (string = 2 characters) (required) ISO 3166-2 alpha-2 country code
            city: (string) The city to ship to
            is_business: (boolean) If delivering to a business in the US (default: False)
            is_postbox: (boolean) Restrict shipping options to options that support post box delivery
            name: (string) The full name of the person
            organization: (string) (semi-required) The name of the organization. Required if "name" is not given
            phone_number: (string <= 20 characters) The phone number of the person
            postcode: (string <= 64 characters) The postal code of the address
            state: (string = 2 or 3 characters) The ISO 3166-2 subdivision code for the state the address is in
            street1: (string) (required) The first street line
            street2: (string) The second street line
        }
    currency: (string) The currency that costs should be calculated in (default: "USD")

    The JSON response contains:
    {
        business_only: (boolean) (required) (default: False) If delivery would only occur on a working day
        cost_excl_tax: (string) The shipping cost excluding tax
        currency: (string) The currency the cost calculations are being done in
        home_only: (boolean) (required) (default: False) If delivery is possible on a non-working day
        id: (integer) (required) The id of the print-job
        level: (string) (required) (default: "MAIL") The shipping level, one of "MAIL" "PRIORITY_MAIL" "GROUND_HD" "GROUND_BUS" "GROUND" "EXPEDITED" "EXPRESS"
        max_delivery_date: (string ISO 8601) (required) The latest estimated delivery date
        max_dispatch_date: (string ISO 8601) The latest estimated dispatch (move to delivery carrier) date
        min_delivery_date: (string ISO 8601) The earliest estimated delivery date
        min_dispatch_date: (string ISO 8601) The earliest estimated dispatch (move to delivery carrier) date
        postbox_ok: (boolean) (required) (default: False) If delivery to postboxes is supported
        total_days_max: (integer) Highest estimate of total business days from start of production to delivery
        total_days_min: (integer) Lowest estimate of total business days from start of production to delivery
        traceable: (boolean) (required) (default: False) If this shipment provides the possibility of a tracking link
        transit_time: (integer) (required) (default: 0) Average transit time in days
    }

    OR
    {
        detail: (string) (required) Details about the error message
    }


# This function sets up a webhook for a developer to have information sent to a url of their choice. Lulu's documentation
# on their API page was a little more limited than I would have liked, so there are some gaps in information for all of
# the webhook functions.
subscribe_to_webhooks(topics, destination_url): Returns a dictionary detailing information about the webhook you subscribed to
    topics: (list of strings) The topic names that you wish to subscribe to. There is little documentation on Lulu about what the options for this parameter are. "PRINT_JOB_STATUS_CHANGED" is an example, but is the only example given.
    destination_url: (string) The url you want the webhook to be sent to.

    The JSON response contains (all items required):
    {
        id: (string uuid) The id of the webhook
        is_active: (boolean) True if the webhook is currently active, False if it is inactive
        topics: (list of strings) The topics that the webhook is following
        url: (string) The url the webhook is sending topics to
    }

    OR
    {
        detail: (string) (required) The error message
    }


# This function gives all of the webhooks you have set up.
get_webhooks(): Returns a dictionary containing information about all of the webhooks that you have set up.
    The JSON response contains:
    {
        count: (integer) (required) The number of webhooks that you have set up
        next: (string) (???)  A link containing something, not sure what
        previous: (string) (???) A link containing something, not sure what
        results: (list of dictionaries) (required) The result of the search
            Each dictionary is identical to the response of subscribe_to_webhooks()
    }

    OR
    {
        detail: (string) (required) The error message
    }


# This function returns a single webhook. The webhook ID is given in the response when you first set up a webhook, or
# in get_webhooks().
get_single_webhook(id): Returns a dictionary containing information about a single webhooks
    id: (string) (required) The id of the webhook

    The JSON response is identical to the response of subscribe_to_webhooks()

    OR
    {
        detail: (string) (required) The error message
    }


# This function updates the information attached to a webhook to the information you pass in the parameters.
# Use this function to change the topics the webhook is subscribed to, the url the webhook is sending information to, or whether or not it is active.
update_webhook(id, topics, destination_url, is_active): Returns a dictionary containing the updated status of a webhook
    id: (string) (required) The id of the webhook
    topics: (list of strings) The topics the webhook will be subscribed to
    destination_url: (string) The url the webhook will be sent to
    is_active: (boolean)  Whether or not you want to the webhook to be active. Status changes to whichever state you give here.

    The JSON response is identical to the response of subscribe_to_webhooks()

    OR
    {
        detail: (string) (required) The error message
    }

    OR
        Some other error format. Printing the response should make the error evident.


# This function permanently deletes a webhook given at ID.
delete_webhook(id): Deletes the webhook at the id, returns nothing
    id: (string) (required) The id of the webhook

    There is no response on success. On failure:
    {
        detail: (string) (required) The error message
    }


# This function triggers a webhook to send an update to the url it is attached to. Use this function during testing to
# have it update such that you can see how your webpage reacts. The topic string is used to identify which topic you
# are trying to test, such as "PRINT_JOB_STATUS_CHANGED"
test_webhook(id, topic): Used to test webhooks, returns a success message on success.
    id: (string) (required) The id of the webhook
    topic: (string) (required) The topic that you wish to have the webhook test. This will be the topic that is sent with the webhook update.

    On success, this function returns a simple string ("Test webhook submission queued"). On failure:
    {
        detail: (string) (required) The error message
    }
    OR
    Some other error format. Printing the response should make the error evident.


# This function gets all of the webhook messages that have been sent to webhooks you own. You can filter the results using the
# parameters for this function, but none of them are required.
get_webhook_submissions(page, page_size, created_after, created_before, is_success, response_code, webhook_id): Returns a dictionary containing the results of a search for webhook submissions
    page: (integer) (default=1) The result page
    page_size: (integer) (default=100) The number of results on a page
    created_after: (string ISO 8601) Gives only the webhook messages sent after the given timestamp
    created_before: (string ISO 8601) Gives only the webhook messages sent before the given timestamp
    is_success: (boolean) Gives only the webhook messages with success status equal to this filter (gives successful messages if this is filter to "True", gives unsuccessful messages if this filter is set to "False")
    response_code: (string) Gives only the webhook messages with a response code equal to this filter (200, 401, 403, 404...)
    webhook_id: (string uuid) Gives only the webhook messages sent from the webhook with the id given in this filter

    The JSON response contains:
    {
        count: (integer) (required) The number of results on the page
        next: (string) (???) A link containing something, not sure what
        previous: (string) (???) A link containing something, not sure what
        results: (list of dictionaries) (required) The result of the search
            Each dictionary contains:
            {
                date_created: (string ISO 8601) (required) The timestamp of the message being created
                date_modified: (string ISO 8601) (required) The timestamp of the message being modified (I don't know why or how a webhook message would be modified, and in the example this string was identical to date_created. Possible that this is always identical to date_created)
                payload: (dictionary) (required) The message that was sent
                    This dictionary contains:
                    {
                        "data": (Unknown) Lulu does not say what this might be. In the example, this field is blank, and so is probably not necessary.
                        "topic": (string) The topic that the message was sending ("PRINT_JOB_STATUS_CHANGED", etc)
                    }
                topic: (string) (required) The topic that was sent with the webhook ("PRINT_JOB_STATUS_CHANGED", etc)
                is_success: (boolean) (required) Whether or not the message was successful
                response_code: (integer) The response code (200, 401, 403, 404..)
                attempts: (integer) (required) The number of attempts at sending the message
                webhook: (dictionary) (required) Information about the webhook the message was sent from
                    This dictionary is identical to the response of subscribe_to_webhooks()
            }
    }
    OR
    {
        detail: (string) (required) The error message
    }

"""

"""
===================
Simplified Lulu API
===================

The simplified Lulu API system rewrites all of the functions to take a single, Master dictionary parameter in place of needing to format all of your data yourself.
The functions will then return an updated version of that same dictionary based on the information returned by Lulu.

The Master Dictionary: This is the dictionary that will be all the inputs and outputs for an individual print-job. Functions that return multiple print-jobs will return a list of master dictionaries.

{
    id: The id of the print-job
    external_id: The id you attached to the print-job
    line_items: [{
        id: (integer) Lulu's identifier for the print-job
        printable_id: (string uuid) The id of the printable
        external_id: (string) A unique, arbitrary identifier that Lulu does not use, but can be used on the developer end for identification purposes
        quantity: (integer) Quantity of printed books for this line item
        title: (string <= 255 characters) The title of the line-item, and should be what appears on the cover of the book
        tracking_urls: (string OR list of strings) All of the tracking urls
        tracking_id: (string) The tracking id of this line item
        carrier_name: (string) The name of the carrier handling the shipment
        status: (string) The status of the print-job
        status_info: (dictionary) The status of the line item, containing the item processing status along with additional information {
            delay: The expected delay due to the error
            error: The error classification
            info: Additional information about the error 
            cover_errors: A list of strings containing information about the errors in the cover file
            interior_errors: A list of strings containing information about the errors in the interior file
            timestamp: The last time the status was updated
        }
        print_information: {
            cover: {
                job_id: The id of the print-job the book is attached to
                file_id: The id of the file that is being used
                filename: The name of the file
                source_md5_sum: (string) The md5 hash of the source file, checking its integrity
                source_url: (string) (required) The url of the source file
            }
            interior: {
                job_id: The id of the print-job the book is attached to 
                file_id: the id of the file that is being used
                filename: the name of the file
                source_md5_sum: (string) The md5 hash of the source file, checking its integrity
                source_url: (string) (required) The url of the source file
            }
        }
        reprint_info: {
            defect: (string) The classification of the defect
            description: (string) Information about the defect
            cost_center: No documentation provided
            printer_at_fault: No documentation provided
        }
    }]
    child_job_ids: (list of integers) The ids of any reprints of this print-job
    parent_job_id: (integer) If this item is a reprint, the original print-job id will be listed here.
    date_created: (string) The date the item was created
    date_modified: (string) The date the item was modified
    contact_email: (string) (required) The contact email if shipping questions arise. This should not be the person you are shipping to, rather it should be you, the distributor/developer.
    order_id: (string) The reference to this order, created when the order is created
    production_delay: (integer between 60 (default) and 2880) The number of minutes that the order is delayed prior to being sent to production. Lulu creates an artificial delay prior to beginning production so that orders can be canceled. After being sent to production, orders can no longer be canceled.
    production_due_time: (string, ISO 8601 timestamp) The target timestamp for when this item will move into production
    shipping_information: {
        city: (string) (required) The city to ship to
        country_code: (string) (required) A two-letter country code adhering to ISO 3166-2 standard (https://en.wikipedia.org/wiki/ISO_3166-2)
        country: Equivalent to country_code
        level: The shipping level to use
        email: (string) The email address that all shipping questions should be sent to. This is NOT the customer, it is you, the developer/business owner.
        is_business: (boolean, defaulted to False) Unless you are shipping to a business, do not include this flag. Some shipping carriers do not deliver to businesses on some days, making this flag sometimes important.
        name: (string) (semi-required) The first and last name of the person. Not required, but at least one of name or organization is required.
        organization: (string) (semi-required) The name of the organization to deliver to. Not required, but at least one of name or organization is required.
        phone_number: (string <= 20 characters) (required) The phone number of the person to deliver to. Lulu does not use this, but it is required by their mail carriers. If this is not here, they will not deliver it. Must match Validation Regex Pattern: ^\+?[\d\s\-.\/()]{8,20}$
        postcode: (string <= 64 characters) (required) The postal code
        state_code: (string of 2 or 3 characters) (semi-required) The 2 or 3 letter state codes (ISO-3166-2 subdivision codes) that are required for some countries, such as the US, Canada, Mexico...
        state: Identical to state code
        street1: (string) (required) The first address line
        street2: (string) The second address line
        title: (string, one of "MR", "MISS", "MRS", "MS", or "DR") The title of the person
        arrival_max: (string) The slowest estimated delivery date
        arrival_min: (string) The fasted estimated delivery date
        dispatch_max: (string) The slowest estimated ship date
        dispatch_min: (string) The fasted estimated ship date
        recipient_tax_id: (string) (required for deliveries in Brazil, Chile, and Mexico) The recipients tax identification number
        warnings: {
            type: (string) The type of warning
            code: (string) A warning code that describes what was suggested by validation
            path: (string) Describes the validation origin of the warning
            message: (string) The warning message that includes the suggested change
        }
        suggested_address: {
            country_code: (string) The country code that was suggested by validation
            state_code: (string) The state code that was suggested by validation
            postcode: (string) The postcode that was suggested by validation
            city: (string) The city that was suggested by validation
            street1: (string) The 1st street line that was suggested by validation
            street2: (string) The 2nd street line that was suggested by validation
        }
    }
    cost_information: {
        currency: (string) The currency for the costs
        total_cost_excl_tax: (string) (required) The total cost of the order without taxes applied
        total_cost_incl_tax: (string) (required) The total cost of the order with taxes applied
        total_discount_amount: (string) (required) The total discount applied
        total_tax: (string) (required) The total tax applied
        shipping_cost: {
            tax_rate: (string) The tax rate applied on shipping and handling
            total_cost_excl_tax: (string) The total cost of the order without taxes applied
            total_cost_incl_tax: (string) The total cost of the order with taxes applied
            total_tax: (string) The total tax applied
        }
        fulfillment_cost: {
            tax_rate: (string) The tax rate applied on shipping and handling
            total_cost_excl_tax: (string) The total cost of the order without taxes applied
            total_cost_incl_tax: (string) The total cost of the order with taxes applied
            total_tax: (string) The total tax applied
        }
        line_item_costs: [{
            cost_excl_discounts: (string) Per unit cost without any discounts applied.
            discounts: (array of dictionaries) A list of the discounts applied for each item, if applicable. Each dictionary contains an "amount" (string) and a "description" (string)
            quantity: (integer) The number of items being printed that all calculations are based on
            tax_rate: (string) The applied tax rate
            total_cost_excl_discounts: (string) The total cost of the order without discounts applied
            total_cost_excl_tax: (string) The total cost of the order without taxes applied
            total_cost_incl_tax: (string) The total cost of the order with taxes applied
            total_tax: (string) The total tax applied
            unit_tier_cost: (string) Per unit cost with tier discount applied. Not applicable for non-tier (list-price) customers.
        }]
    }
}


create_print_job(input_dictionary):
    The input_dictionary contains:
        line_items: [{
            cover: (string) (required) The url of the cover file
            interior: (string) (required) The url of the interior file
        }]
        shipping_information: {
            city: (string) (required) The city to ship to
            country_code: (string) (required) A two-letter country code adhering to ISO 3166-2 standard (https://en.wikipedia.org/wiki/ISO_3166-2)
            country: Equivalent to country_code
            level: The shipping level to use
            email: (string) The email address that all shipping questions should be sent to. This is NOT the customer, it is you, the developer/business owner.
            is_business: (boolean, defaulted to False) Unless you are shipping to a business, do not include this flag. Some shipping carriers do not deliver to businesses on some days, making this flag sometimes important.
            name: (string) (semi-required) The first and last name of the person. Not required, but at least one of name or organization is required.
            organization: (string) (semi-required) The name of the organization to deliver to. Not required, but at least one of name or organization is required.
            phone_number: (string <= 20 characters) (required) The phone number of the person to deliver to. Lulu does not use this, but it is required by their mail carriers. If this is not here, they will not deliver it. Must match Validation Regex Pattern: ^\+?[\d\s\-.\/()]{8,20}$
            postcode: (string <= 64 characters) (required) The postal code
            state_code: (string of 2 or 3 characters) (semi-required) The 2 or 3 letter state codes (ISO-3166-2 subdivision codes) that are required for some countries, such as the US, Canada, Mexico...
            street1: (string) (required) The first address line
            street2: (string) The second address line
            title: (string, one of "MR", "MISS", "MRS", "MS", or "DR") The title of the person
            recipient_tax_id: (string) (required for deliveries in Brazil, Chile, and Mexico) The recipients tax identification number
        }
        external_id: (string) An arbitrary string that use can use for yourself to identify the print-job
        production_delay: (integer) (default = 60) The delay between Lulu receiving a print-job and sending it to the printers, in minutes.
    
    You receive a simple dictionary in return.
    

get_print_jobs(filters):
    filters is identical to the lulu_get_print_jobs function
    
    The return dictionary is identical to lulu_get_print_jobs, but each entry in results is in the simplified form.
    
get_print_jobs(id): 
    id: (string) (required) The id of the print-job
    
    You receive a simple dictionary in return.

"""


import requests
import LuluAPI.lulu_token as token
import json

SANDBOX = token.SANDBOX

if SANDBOX:
    URLPREFIX = "https://api.sandbox.lulu.com/"
else:
    URLPREFIX = "https://api.lulu.com/"

auth_key = token.get_token()

post_headers = {
    "Authorization": f"Bearer {auth_key}",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json"
}

get_headers = {
    "Authorization": f"Bearer {auth_key}",
    "Cache-Control": "no-cache",
}

# This function takes a dictionary from Lulu from either the get_print_job() or get_print_jobs() function.
# Since the response schema is different for create_print_job, this function won't work on that.
def convert_print_job(lulu_dictionary):
    line_items = []
    for item in lulu_dictionary["line_items"]:
        line_item = {
            "id": item["id"], #
            "printable_id": item["printable_id"],#
            "external_id": item["external_id"], #
            "quantity": item["quantity"], #
            "title": item["title"], #
            "status": item["status"]["name"], #
            "tracking_urls": item["status"]["messages"].get("tracking_urls"),
            "tracking_id": item["status"]["messages"].get("tracking_id"),
            "carrier_name": item["status"]["messages"].get("carrier_name"),
            "status_info": {
                "delay": item["status"]["messages"].get("delay"),
                "error": item["status"]["messages"].get("error"),
                "info": item["status"]["messages"].get("info"),
                "cover_errors": item["status"]["messages"].get("printable_normalization", {}).get("cover"),
                "interior_errors": item["status"]["messages"].get("printable_normalization", {}).get("interior"),
                "timestamp": item["status"]["messages"].get("timestamp"),
            },
            "print_information": {
                "cover": {
                    "job_id": item["printable_normalization"]["cover"].get("job_id"),
                    "file_id": (item["printable_normalization"]["cover"].get("normalized_file", {}) or {}).get("file_id"),
                    "filename": (item["printable_normalization"]["cover"].get("normalized_file", {}) or {}).get("filename"),
                    "source_md5_sum": item["printable_normalization"]["cover"].get("source_md5_sum"),
                    "source_url": item["printable_normalization"]["cover"].get("source_url"),
                },
                "interior": {
                    "job_id": item["printable_normalization"]["interior"].get("job_id"),
                    "file_id": (item["printable_normalization"]["interior"].get("normalized_file", {}) or {}).get("file_id"),
                    "filename": (item["printable_normalization"]["interior"].get("normalized_file") or {}).get(
                        "filename"),
                    "source_md5_sum": item["printable_normalization"]["interior"].get("source_md5_sum"),
                    "source_url": item["printable_normalization"]["interior"].get("source_url"),
                }
            },
            "reprint_info": {
                "defect": (item.get("reprint_info") or {}).get("defect"),
                "description": (item.get("reprint_info") or {}).get("description"),
                "cost_center": (item.get("reprint_info") or {}).get("cost_center"),
                "printer_at_fault": (item.get("reprint_info") or {}).get("printer_at_fault"),
            }
        }
        line_items.append(line_item)

    return_dictionary = {
        "id": lulu_dictionary["id"],
        "external_id": lulu_dictionary["external_id"],
        "line_items": line_items,
        "child_job_ids": lulu_dictionary.get("child_job_ids"),
        "parent_job_id": lulu_dictionary.get("parent_job_id"),
        "date_created": lulu_dictionary.get("date_created"),
        "date_modified": lulu_dictionary.get("date_modified"),
        "contact_email": lulu_dictionary["contact_email"],
        "order_id": lulu_dictionary.get("order_id"),
        "production_delay": lulu_dictionary.get("production_delay"),
        "production_due_time": lulu_dictionary.get("production_due_time"),
        "shipping_information": {
            "city": lulu_dictionary["shipping_address"]["city"],
            "country_code": lulu_dictionary["shipping_address"]["country_code"],
            "country": lulu_dictionary["shipping_address"]["country_code"],
            "level": lulu_dictionary["shipping_level"],
            "email": lulu_dictionary["shipping_address"]["email"],
            "is_business": lulu_dictionary["shipping_address"]["is_business"],
            "name": lulu_dictionary["shipping_address"].get("name"),
            "organization": lulu_dictionary["shipping_address"].get("organization"),
            "phone_number": lulu_dictionary["shipping_address"]["phone_number"],
            "postcode": lulu_dictionary["shipping_address"]["postcode"],
            "state_code": lulu_dictionary["shipping_address"]["state_code"],
            "state": lulu_dictionary["shipping_address"]["state_code"],
            "street1": lulu_dictionary["shipping_address"]["street1"],
            "street2": lulu_dictionary["shipping_address"].get("street2"),
            "title": lulu_dictionary["shipping_address"].get("title"),
            "arrival_max": (lulu_dictionary["estimated_shipping_dates"] or {}).get("arrival_max"),
            "arrival_min": (lulu_dictionary["estimated_shipping_dates"] or {}).get("arrival_min"),
            "dispatch_max": (lulu_dictionary["estimated_shipping_dates"] or {}).get("dispatch_max"),
            "dispatch_min": (lulu_dictionary["estimated_shipping_dates"] or {}).get("dispatch_min"),
            "recipient_tax_id": lulu_dictionary["shipping_address"].get("recipient_tax_id"),
            "warnings": lulu_dictionary["shipping_address"].get("warnings"),
            "suggested_address": lulu_dictionary["shipping_address"].get("suggested_address"),
        },
        "cost_information": {
            "currency": lulu_dictionary["costs"]["currency"],
            "total_cost_excl_tax": lulu_dictionary["costs"]["total_cost_excl_tax"],
            "total_cost_incl_tax": lulu_dictionary["costs"]["total_cost_incl_tax"],
            "total_tax": lulu_dictionary["costs"]["total_tax"],
            "shipping_cost": lulu_dictionary["costs"]["shipping_cost"],
            "fulfillment_cost": lulu_dictionary["costs"]["fulfillment_cost"],
            "line_item_costs": lulu_dictionary["costs"]["line_item_costs"],
        }
    }
    return return_dictionary


# SUPER IMPORTANT: This key tells lulu all the details about how we want the book to be printed, including size, finish, etc.
# You can generate this key on the price calculator website. Look for "SKU" followed by a 27-digit code.
def make_sku_id(gloss):
    if gloss == "matte":
        pod_package_id = "0850X1100FCPRECW080CW444MXX"
    elif gloss == "glossy":
        pod_package_id = "0850X1100FCPRECW080CW444GXX"
    else:
        raise TypeError("gloss must be either 'matte' or 'glossy'")
    return pod_package_id

def post_interior_file_validation(link, pod_package_id=""):
    payload = json.dumps({
        "source_url": link,
        "pod_package_id": pod_package_id
    })
    url = f"{URLPREFIX}validate-interior/"
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def get_interior_file_validation(id):
    url = f"{URLPREFIX}validate-interior/{id}"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def post_cover_file_validation(link, pod_package_id, interior_page_count):
    url = f"{URLPREFIX}validate-cover/"
    payload = json.dumps({
        "source_url": link,
        "pod_package_id": pod_package_id,
        "interior_page_count": interior_page_count
    })
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def get_cover_file_validation(id):
    url = f"{URLPREFIX}validate-cover/{id}"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def calculate_print_job_cost(line_items, shipping_address, shipping_option):
    url = f"{URLPREFIX}print-job-cost-calculations/"
    payload = json.dumps({
        "line_items": line_items,
        "shipping_address": shipping_address,
        "shipping_option": shipping_option
    })
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def get_print_jobs(filters=None):
    lulu_response = lulu_get_print_jobs(filters)
    for index, item in enumerate(lulu_response["results"]):
        lulu_response["results"][index] = convert_print_job(item)
    return lulu_response

def lulu_get_print_jobs(filters=None):
    url = f"{URLPREFIX}print-jobs/"
    payload = {}
    if filters is None:
        filters = {}
    response = requests.request("GET", url, headers=get_headers, data=payload, params=filters)
    return response.json()

def create_print_job(input_info):
    lulu_dictionary = lulu_create_print_job(input_info["line_items"], input_info["shipping_information"], input_info["shipping_information"]["level"], input_info["shipping_information"]["email"], input_info["external_id"], input_info["production_delay"])
    new_shipping_information = input_info["shipping_information"]
    new_shipping_information["warnings"] = lulu_dictionary["shipping_address"]["warnings"]
    new_shipping_information["suggested_address"] = lulu_dictionary["shipping_address"]["suggested_address"]
    line_items = []
    for item in lulu_dictionary["line_items"]:
        line_item = {
            "id": item["id"],
            "printable_id":item["printable_id"],
            "external_id": item["external_id"],
            "quantity":item["quantity"],
            "title":item["title"],
            "status": item["status"]["name"],
            "timestamp": None,
            "tracking_urls": item["tracking_urls"],
            "tracking_id": item["tracking_id"],
            "carrier_name": None,
            "status_info": {
                "delay": item["status"]["messages"].get("delay"),
                "error": item["status"]["messages"].get("error"),
                "info": item["status"]["messages"].get("info"),
                "cover_errors": item["status"]["messages"].get("printable_normalization", {}).get("cover"),
                "interior_errors": item["status"]["messages"].get("printable_normalization", {}).get("interior"),
            },
            "print_information": {
                "cover": {
                    "job_id": item["printable_normalization"]["cover"].get("job_id"),
                    "file_id": item["printable_normalization"]["cover"].get("file_id"),
                    "filename": (item["printable_normalization"]["cover"].get("normalized_file", {}) or {}).get("filename"),
                    "source_md5_sum": item["printable_normalization"]["cover"].get("source_md5_sum"),
                    "source_url":item["printable_normalization"]["cover"].get("source_url"),
                },
                "interior": {
                    "job_id": item["printable_normalization"]["interior"].get("job_id"),
                    "file_id": item["printable_normalization"]["interior"].get("file_id"),
                    "filename": (item["printable_normalization"]["interior"].get("normalized_file") or {}).get("filename"),
                    "source_md5_sum": item["printable_normalization"]["interior"].get("source_md5_sum"),
                    "source_url": item["printable_normalization"]["interior"].get("source_url"),
                }
            },
            "reprint_info": {
                "defect": None,
                "description": None,
                "cost_center":None,
                "printer_at_fault": None,
            }
        }

        line_items.append(line_item)

    return_dictionary = {
        "id": lulu_dictionary["id"],
        "external_id": lulu_dictionary["external_id"],
        "line_items": line_items,
        "child_job_ids": None,
        "parent_job_id": None,
        "date_created": None,
        "date_modified": None,
        "contact_email": lulu_dictionary["contact_email"],
        "order_id": lulu_dictionary["order_id"],
        "production_delay": lulu_dictionary["production_delay"],
        "production_due_time": lulu_dictionary["production_due_time"],
        "shipping_information": new_shipping_information,
        "cost_information": {
            "currency": None,
            "total_cost_excl_tax": lulu_dictionary["costs"]["total_cost_excl_tax"],
            "total_cost_incl_tax": lulu_dictionary["costs"]["total_cost_incl_tax"],
            "total_tax": lulu_dictionary["costs"]["total_tax"],
            "shipping_cost": lulu_dictionary["costs"]["shipping_cost"],
            "fulfillment_cost": {
                "tax_rate": None,
                "total_cost_excl_tax": None,
                "total_cost_incl_tax": None,
                "total_tax": None,
            },
            "line_item_costs": lulu_dictionary["costs"]["line_item_costs"],

        }
    }
    return return_dictionary

def lulu_create_print_job(line_items, shipping_address, shipping_level, contact_email, external_id="", production_delay=60):
    url = f"{URLPREFIX}print-jobs/"
    payload = json.dumps({
        "line_items": line_items,
        "shipping_address": shipping_address,
        "shipping_level": shipping_level,
        "contact_email": contact_email,
        "external_id": external_id,
        "production_delay": production_delay
    })
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def get_print_job_statistics(filters=None):
    url = f"{URLPREFIX}print-jobs/statistics/"
    payload = {}
    if filters is None:
        filters = {}
    response = requests.request("GET", url, headers=get_headers, data=payload, params=filters)
    return response.json()

def get_single_print_job(id):
    lulu_dictionary = lulu_get_single_print_job(id)
    return convert_print_job(lulu_dictionary)

def lulu_get_single_print_job(id):
    url = f"{URLPREFIX}print-jobs/{id}/"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def get_print_job_cost(id):
    url = f"{URLPREFIX}print-jobs/{id}/costs/"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def get_print_job_status(id):
    url = f"{URLPREFIX}print-jobs/{id}/status/"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def cancel_print_job(id):
    url = f"{URLPREFIX}print-jobs/{id}/status/"
    payload = json.dumps({
        "name": "CANCELED"
    })
    response = requests.request("PUT", url, headers=post_headers, data=payload)
    return response.json()

def retrieve_shipping_options(line_items, shipping_address, currency="USD"):
    url = f"{URLPREFIX}shipping-options/"
    payload = json.dumps({
        "line_items": line_items,
        "shipping_address": shipping_address,
        "currency": currency
    })
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def subscribe_to_webhooks(topics, destination_url):
    url = f"{URLPREFIX}webhooks/"
    payload = json.dumps({
        "topics": topics,
        "url": destination_url
    })
    response = requests.request("POST", url, headers=post_headers, data=payload)
    return response.json()

def get_webhooks():
    url = f"{URLPREFIX}webhooks/"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def get_single_webhook(id):
    url = f"{URLPREFIX}webhooks/{id}/"
    payload = {}
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()

def update_webhook(id, topics=None, destination_url=None, is_active=None):
    url = f"{URLPREFIX}webhooks/{id}/"
    payload = {}
    if topics is not None:
        payload["topics"] = topics
    if destination_url is not None:
        payload["url"] = destination_url
    if is_active is not None:
        payload["is_active"] = is_active
    response = requests.request("PATCH", url, headers=post_headers, json=payload)
    return response.json()

def delete_webhook(id):
    url = f"{URLPREFIX}webhooks/{id}/"
    payload = {}
    response = requests.request("DELETE", url, headers=get_headers, data=payload)
    return response.json()

def test_webhook(id, topic):
    url = f"{URLPREFIX}webhooks/{id}/test-submission/{topic}"
    payload = {}
    response = requests.request("POST", url, headers=get_headers, data=payload)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return None

def get_webhook_submissions(page=1, page_size=100, created_after=None, created_before=None, is_success=None, response_code=None, webhook_id=None):
    url = f"{URLPREFIX}webhook-submissions/"
    payload = json.dumps({
        "page": page,
        "page_size": page_size,
        "created_after": created_after,
        "created_before": created_before,
        "is_success": is_success,
        "response_code": response_code,
        "webhook_id": webhook_id
    })
    response = requests.request("GET", url, headers=get_headers, data=payload)
    return response.json()
