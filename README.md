### Rent Management System

Rent Management System

A [Frappe](https://frappe.io) app to manage rooms, tenants, monthly rent invoices and rent collection.

### Features

- **Tenant** - contact, personal (with Aadhaar checksum validation) and professional details.
- **Tenant Space Type / Tenant Space** - room types with standard rent and security deposit, and rooms with live
  occupancy status (Available / Reserved / Occupied / Under Renovation).
- **Tenant Space Allotment** - allots a room to a tenant. Submitting it marks the room Occupied; the **Vacate**
  button records the move-out date and frees the room. A room cannot be allotted to two tenants at once.
- **Tenant Rent Invoice** - one invoice per allotment per month. Rent is pro-rated for the days actually occupied
  (move-in and move-out months), extra charges (electricity, water, maintenance...) and a discount can be added,
  and the invoice tracks paid / outstanding amount with a status of Unpaid, Partly Paid, Paid or Overdue.
- **Rent Payment** - records a payment (Cash, UPI, Bank Transfer, Cheque...) against an invoice and updates its
  outstanding amount.
- **Security Deposit Settlement** - settles the deposit after the tenant vacates: record deductions (damages,
  cleaning...), optionally use the deposit to pay off unpaid rent (posted as Rent Payments with mode
  *Security Deposit*), and see the refund due to the tenant or the balance they still owe.
- **Rent Outstanding report** - unpaid invoices with days overdue, aging buckets (0-30 / 31-60 / 61-90 / 90+),
  totals and a chart. Filter by tenant, room or overdue only.
- **Rent Manager role** - full access to everything in the app without needing System Manager. Assign it to the
  people who run the property.
- **Rent Management Settings** - rent due day, and automatic monthly invoicing. On the 1st of every month an
  invoice is created for each active allotment (as draft, or submitted). Use **Generate Invoices Now** to run it
  for any month. A daily job marks unpaid invoices past their due date as Overdue.

### Web app (`/rent`)

Besides the Frappe desk, the app ships a Vue 3 + Tailwind frontend for property managers at
**`https://<your-site>/rent`**. It uses the normal Frappe login and is available to users with the
*Rent Manager* or *System Manager* role.

- **Dashboard** - occupancy, collected vs invoiced, outstanding and overdue rent, 6-month collection chart,
  overdue invoices and recent payments.
- **Rooms** - every room as a card with its status, tenant and dues; allot, invoice or vacate in one click.
- **Tenants** - searchable list and a profile page with the current stay, invoices, payments and stay history.
- **Invoices** - filter by status / month, generate the month's invoices, create invoices with extra charges,
  submit drafts, record payments, print, and send a WhatsApp reminder.
- **Payments**, **Deposits** (collect, then settle with a live refund preview) and **Outstanding** (aging buckets).

The frontend talks to the whitelisted methods in `rent_management/api.py`, which run every change through the
regular DocType validations.

`bench build` builds the frontend automatically. To work on it with hot reload:

```bash
cd apps/rent_management/frontend
yarn install
yarn dev   # http://localhost:8080/rent/, proxies API calls to the Frappe server on :8000
```

Log in on the Frappe server first. The dev server can't inject a CSRF token, so set `"ignore_csrf": 1` in the
site's `site_config.json` while developing (never in production).

### Workflow

1. Create **Tenant Space Types** and **Tenant Spaces** (rooms).
2. Create a **Tenant**.
3. Create and submit a **Tenant Space Allotment** for the tenant and room.
4. Rent invoices are generated every month (or use *Create > Rent Invoice* on the allotment).
5. Submit the invoice, then use *Create > Rent Payment* on it to record what the tenant paid.
6. When the tenant moves out, click **Vacate** on the allotment; the last invoice is pro-rated to the vacate date.
7. Tick **Deposit Collected** on the allotment when you receive the deposit. After vacating, use
   *Create > Deposit Settlement* to settle it.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app rent_management
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/rent_management
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
