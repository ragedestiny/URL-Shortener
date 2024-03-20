# URL Shortener CLI Usage Guide

## Overview

This CLI tool provides a convenient way to interact with the URL shortener service. It offers various commands to perform actions such as shortening URLs, listing URLs, updating URL limits, logging in, creating users, and more.

## Installation

To install the URL Shortener CLI, follow these steps:

1. Make sure you have Python installed on your system.
2. Clone the repository:

   ```bash
   git clone https://github.com/ragedestiny/URL-Shortener.git
   ```

3. Navigate to the project directory:

   ```bash
   cd url-shortener
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Commands

### User

The user app provides commands for user-specific tasks.

#### 1. Create User

This command creates a new user account.

Usage:

    ```bash
    python app\main.py user create-user <email> <password>
    ```

#### 2. List My URLs

This command lists URLs associated with the authenticated user.

Usage:

    ```bash
    python app\main.py user list-my-urls <access_token>
    ```

#### 3. Change Password

This command changes the password for the authenticated user.

Usage:

    ```bash
    python app\main.py user change-password <new_password> <access_token>
    ```

#### 4. Shorten URL

This command shortens a long URL.

Usage:

    ```bash
    python app\main.py user shorten-url <long_url> <access_token> [--short_url <short_url>]
    ```

Note: The `--short_url` option is optional and can be used to specify a custom short URL.

#### 5. Shorten URL

This command deletes a URL created by its user.

Usage:

    ```bash
    python app\main.py user delete-url <short_url> <access_token>
    ```

### Auth

The auth app provides commands for authentication-related tasks.

#### 1. Login

This command logs in and retrieves an access token.

Usage:

    ```bash
    python app\main.py auth login <username> <password>
    ```

### Admin

The admin app provides commands for administrative tasks related to the URL shortener service.

#### 1. List All URLs

This command retrieves all short URL to long URL pairs.

Usage:

    ```bash
    python app\main.py admin list-all-urls <access_token>
    ```

#### 2. Update URL Limit

This command updates the URL limit for a user.

Usage:

    ```bash
    python app\main.py admin update-url-limit <user_email> <new_limit> <access_token>
    ```

### URL

The URL app provides commands for managing URLs.

#### 1. Lookup URL

This command looks up the long URL associated with the provided short URL.

Usage:

    ```bash
    $ python app\main.py url lookup-url <short_url>
    ```
