---
name: print-format-development
description: "Create, maintain, convert, or troubleshoot HTML print formats for ERPNext documents (Sales Invoices, Quotations, Purchase Orders, Delivery Notes, etc.) using the becharged Jinja macro system, DIN 5008 layout standards, and Frappe translations. Activate when building or modifying print formats, fixing PDF rendering/footer cutoffs, or synchronizing translations."
argument-hint: "DocType (e.g., Sales Invoice), Print Format name, or task (e.g., convert to macro pattern, fix footer)"
disable-model-invocation: true
---

# Print Format Development for becharged

Create, convert, and maintain standardized HTML print formats for ERPNext documents in the `becharged` application using centralized Jinja macros, DIN 5008 business letter layout, and Frappe internationalization.

## Asset & Macro Locations

- **Central Macros:** `apps/becharged/becharged/becharged/print_format/includes/print_macros.html`
- **Jinja Import Path:** `becharged/becharged/print_format/includes/print_macros.html`
- **Translations:** `apps/becharged/becharged/translations/de.csv`
- **Detailed Macro API Reference:** [references/macros.md](./references/macros.md)

---

## Inputs

| Input | Description | Source | Required? |
|---|---|---|---|
| Target DocType | ERPNext DocType (e.g., `Sales Invoice`, `Quotation`, `Purchase Order`) | User / Task | Yes |
| Print Format Name | Folder and file slug in `print_format/` (e.g., `bch_rechnung`, `bch_angebot`) | Task / Codebase convention | Yes |
| Layout / Field Specs | Header text, item grouping, tax breakdown, custom fields, payment terms | Requirements / DocType schema | No (defaults to standard) |

---

## Workflow

### 1. Initialize Template & Import Macros

Begin every print format template with the standard Jinja macro import and base style call:

```jinja
{%- from "becharged/becharged/print_format/includes/print_macros.html" 
    import common_styles, print_header, recipient_address, customer_address, 
    contact_info, salutation, print_footer, fold_marks -%}

{{ common_styles() }}
```

### 2. Fetch Document Context & Helpers

Retrieve company details, addresses, and contacts in the template preamble:

```jinja
{% set company = frappe.get_doc("Company", doc.company) %}
{% set contact = frappe.get_doc("Contact", doc.contact_person) if doc.contact_person else None %}
{% set currency = frappe.db.get_single_value("System Settings", "currency") %}
{% set precision = 2 %}
{% set flt = frappe.utils.flt %}
```

### 3. Build Header & Contact Row (DIN 5008 Layout)

Render the header logo/letterhead, address block, contact table, and fold marks:

```jinja
<!-- HEADER -->
{{ print_header(letter_head, no_letterhead) }}

<!-- ADDRESS & CONTACT INFO -->
<div class="contact-row">
    {{ recipient_address(doc, contact, False, "customer_name") }}

    {% set extra_contact_rows = [
        {"label": _("Customer number"), "value": doc.customer},
        {"label": _("Contact person"), "value": doc.custom_ansprechpartner if doc.custom_ansprechpartner else frappe.db.get_value("User", frappe.session.user, "full_name")},
        {"label": _("Email"), "value": frappe.db.get_value("User", frappe.session.user, "email")}
    ] %}
    {% set phone = frappe.db.get_value("User", frappe.session.user, "phone") or frappe.db.get_value("User", frappe.session.user, "mobile_no") %}
    {% if phone %}
        {% set _ = extra_contact_rows.append({"label": _("Phone"), "value": phone}) %}
    {% endif %}

    {{ contact_info(doc, _("INVOICE"), _("Receipt number"), "posting_date", extra_contact_rows) }}
</div>

{{ fold_marks() }}
```

### 4. Construct Document Body (`#text`)

Render greeting, introductory text, line items table, totals calculation, and payment terms inside `#text`:

```jinja
<div id="text">
    {{ salutation(contact) }}
    <br>
    {% if doc.custom_header_text %}
        <p>{{ _(doc.custom_header_text) }}</p>
        <br>
    {% endif %}

    <table class="w-100">
        <thead class="black-border">
            <tr>
                <th style="width: 5%">{{ _("Sr") }}</th>
                <th style="width: 43%">{{ _("Description") }}</th>
                <th style="width: 10%">{{ _("Unit") }}</th>
                <th style="width: 10%">{{ _("Qty") }}</th>
                <th style="width: 13%">{{ _("Price") }}</th>
                <th style="width: 13%" class="text-right">{{ _("Amount") }}</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>
                    <b>{{ _(item.item_name) }}</b><br>
                    {{ item.description }}
                </td>
                <td>{{ _(item.uom) }}</td>
                <td>{{ item.get_formatted('qty') }}</td>
                <td>{{ item.get_formatted('rate') }}</td>
                <td class="text-right">{{ item.get_formatted('amount') }}</td>
            </tr>
            {% if not loop.last %}
                <tr><td colspan="6" style="border-top: 1px solid #000; padding: 0;"></td></tr>
            {% endif %}
            {% endfor %}
        </tbody>
    </table>

    <!-- Totals Table -->
    <table class="w-100 black-border">
        <tr>
            <td>{{ _("Total") }}</td>
            <td class="text-right">{{ doc.get_formatted('total') }}</td>
        </tr>
        {% if doc.tax_category == "Reverse Charge" %}
            <tr>
                <td>{{ _("Tax liability of the recipient.") }}</td>
                <td class="text-right"></td>
            </tr>
        {% else %}
            {% for tax in doc.taxes %}
            <tr>
                <td>{{ tax.description }}</td>
                <td class="text-right">{{ tax.get_formatted('tax_amount') }}</td>
            </tr>
            {% endfor %}
        {% endif %}
        <tr>
            <td><strong>{{ _("Grand Total") }}</strong></td>
            <td class="text-right"><strong>{{ doc.get_formatted('grand_total') }}</strong></td>
        </tr>
    </table>
    <br>

    <!-- Payment Terms -->
    <div>
        <p><b>{{ _("Payment terms") }}:</b>
            {% if doc.payment_schedule %}
                {{ doc.payment_schedule[0].description or doc.payment_terms_template or "" }}
                {% if doc.payment_terms_template == "SEPA-Mandat" and doc.custom_sepa_mandate_reference %}
                    {{ _("The mandate reference is") }} {{ doc.custom_sepa_mandate_reference }}.
                {% endif %}
            {% else %}
                {{ _("Payable until") }} {{ frappe.utils.formatdate(doc.due_date, "dd. MMMM yyyy") }}
            {% endif %}
        </p>
    </div>

    {% if doc.terms %}
        <br><div>{{ doc.terms }}</div>
    {% endif %}
</div>
```

### 5. Append Footer

Always close the template with `print_footer`:

```jinja
{{ print_footer(footer) }}
```

### 6. Synchronize Translations

Ensure every user-facing string wrapped in `_("...")` exists in `apps/becharged/becharged/translations/de.csv`.

1. Extract all `_("...")` strings from the template.
2. Check `apps/becharged/becharged/translations/de.csv` for existing entries.
3. Append missing entries using Frappe CSV format:
   ```csv
   English Source Text,German Translation,
   "Text with, comma","Übersetzung mit, Komma",
   ```
4. Reload cache via `bench clear-cache` or `bench restart`.

### 7. Validate & Test

1. **Syntax validation:** Verify all Jinja tag pairs (`{% if %}` / `{% endif %}`, `{% for %}` / `{% endfor %}`) are balanced.
2. **DIN 5008 alignment:** Verify `#header`, `.contact-row`, `#address`, `#contact`, `{{ fold_marks() }}`, `#text`, and `{{ print_footer() }}` elements are intact.
3. **Formatters check:** Confirm all currency, date, and quantity outputs use `doc.get_formatted()`, `item.get_formatted()`, `frappe.format_value()`, or `frappe.utils.formatdate()`.

---

## Decision Rules

| Requirement / Context | Decision & Implementation |
|---|---|
| Customer document (e.g. Sales Invoice, Quotation) | Call `recipient_address(doc, contact, False, "customer_name")` and use `doc.customer` for Customer number row. |
| Supplier document (e.g. Purchase Order, Purchase Invoice) | Call `recipient_address(doc, contact, False, "supplier_name")` and pass `"transaction_date"` or `"bill_date"` to `contact_info`. |
| Shipping address required | Pass `use_shipping=True` to `recipient_address(doc, contact, use_shipping=True)`. |
| Primary date field selection | Invoices: `"posting_date"`. Quotations / POs: `"transaction_date"`. Delivery Notes: `"posting_date"`. Credit Notes: `"posting_date"`. |
| Item grouping with subtotals | Use the Jinja `namespace` accumulator pattern with `Separator` item rows (see Implementation Patterns below). |
| Reverse Charge tax mode | Check `doc.tax_category == "Reverse Charge"`; display `_("Tax liability of the recipient.")` instead of the tax table loop. |
| SEPA Mandate payment terms | If `doc.payment_terms_template == "SEPA-Mandat"`, display mandate reference from `doc.custom_sepa_mandate_reference`. |
| Document-specific styling | Do not modify `print_macros.html`. Place scoped `<style>` tags directly inside the print format file after `{{ common_styles() }}`. |

---

## Macro Summary Reference

All macros reside in `apps/becharged/becharged/becharged/print_format/includes/print_macros.html`.

| Macro | Signature | Key Behavior |
|---|---|---|
| `common_styles()` | `common_styles()` | Injects global CSS for page margins, DIN 5008 positions, table page-breaks, and footer. |
| `print_header()` | `print_header(letter_head=None, no_letterhead=False)` | Emits default becharged logo or custom letterhead HTML in `#header`. |
| `sender_address()` | `sender_address()` | Emits DIN 5008 one-line sender address in `#sender`. (Called automatically inside `recipient_address`). |
| `recipient_address()` | `recipient_address(doc, contact=None, use_shipping=False, recipient_field="customer_name", show_contact=True)` | Emits DIN 5008 window with sender line, recipient name, contact attention line, and full address. |
| `customer_address()` | `customer_address(doc, contact=None, use_shipping=False)` | Convenience wrapper around `recipient_address` for customer documents. |
| `contact_info()` | `contact_info(doc, title, doc_label, date_field="posting_date", extra_rows=[])` | Emits right-aligned metadata table with title, document name, date, and custom row entries. |
| `salutation()` | `salutation(contact=None)` | Renders formal German greeting: `"Sehr geehrte Damen und Herren,"` or `"Sehr geehrte(r) Herr/Frau <Name>,"`. |
| `print_footer()` | `print_footer(footer_content)` | Emits `<div id="footer" class="visible-pdf">` with `.print-format-footer` wrapper. |
| `fold_marks()` | `fold_marks()` | Emits 3 DIN 5008 fold/punch marks at 115mm, 158.5mm, and 220mm. |

*For full argument definitions and HTML outputs, see [references/macros.md](./references/macros.md).*

---

## Key Implementation Patterns

### Grouped Items with Separators (`namespace`)
For complex documents with item groups (e.g. `bch_rechnung`, `bch_angebot`, `bch_einkausauftrag`):

```jinja
{%- set ns = namespace(
    current_group="",
    group_total=0,
    components={},
    group_index=0,
    count=0
) -%}

{% for item in doc.items %}
    {% if item.item_group == "Separator" %}
        {% set ns.group_index = ns.group_index + 1 %}
        {% set ns.count = 0 %}
        {% if ns.current_group != "" %}
            <tr>
                <td></td>
                <td colspan="4">{{ _("Sum") }}: {{ ns.current_group }}</td>
                <td class="text-right">{{ frappe.format_value(ns.group_total, 'Currency') }}</td>
            </tr>
            {% set temp = ns.components.copy() %}
            {% set _ = temp.update({ns.current_group: ns.group_total}) %}
            {% set ns.components = temp %}
            {% set ns.group_total = 0 %}
        {% endif %}
        <tr class="section_heading">
            <td>{{ ns.group_index }}</td>
            <td colspan="5"><b>{{ item.item_name }}</b></td>
        </tr>
        {% set ns.current_group = item.item_name %}
    {% else %}
        {% set ns.count = ns.count + 1 %}
        {% set ns.group_total = flt(ns.group_total + flt(item.amount, precision), precision) %}
        <tr>
            <td>{{ ns.group_index ~ "." ~ ns.count }}</td>
            <td><b>{{ _(item.item_name) }}</b><br>{{ item.description }}</td>
            <td>{{ _(item.uom) }}</td>
            <td>{{ item.get_formatted('qty') }}</td>
            <td>{{ item.get_formatted('rate') }}</td>
            <td class="text-right">{{ item.get_formatted('amount') }}</td>
        </tr>
    {% endif %}
{% endfor %}
```

### Supplier / Purchase Order Documents
For supplier-facing documents (e.g., Purchase Order `bch_einkausauftrag`, Purchase Invoice `bch_einkaufsrechnung`), pass `recipient_field="supplier_name"`:

```jinja
{{ recipient_address(doc, contact, False, "supplier_name") }}
{{ contact_info(doc, _("PURCHASE ORDER"), _("Receipt number"), "transaction_date", extra_contact_rows) }}
```

---

## Constraints

1. **Never hardcode German text in templates:** Always wrap user-visible text in `_("...")` and translate in `de.csv`.
2. **Do not modify `print_macros.html` for single-document styling:** Use custom `<style>` overrides inside the specific print format file instead.
3. **Respect DIN 5008 layout:** Maintain the `.contact-row` container, `#address` (left float), `#contact` (right float), and `{{ fold_marks() }}`.
4. **Use Frappe formatters:** Use `frappe.utils.formatdate(doc.date, "dd. MMMM yyyy")` and `item.get_formatted(...)` / `frappe.format_value(val, 'Currency')` to ensure locale compliance.
5. **Preserve PDF footer classes:** Always use `{{ print_footer(footer) }}` to retain `.visible-pdf` and prevent footer cutoffs in `wkhtmltopdf`.

---

## Failure Handling

| Failure / Issue | Root Cause | Resolution |
|---|---|---|
| `jinja2.exceptions.UndefinedError` on field | DocType field is empty, unlinked, or undefined | Use `doc.get('field_name')` or guard with `{% if doc.field_name %}` before accessing nested attributes. |
| Recipient address block empty or broken | `doc.customer_address` / `doc.supplier_address` unlinked | Verify address link on document; `recipient_address` macro will fall back to `doc.address_display`. |
| Salutation defaults to generic ("Sehr geehrte Damen und Herren") | `doc.contact_person` unlinked or Contact lacks `salutation`/`last_name` | Ensure Contact record has `salutation` and `last_name` populated, or check `doc.contact_display`. |
| Footer cut off or missing in PDF | Missing `visible-pdf` class or custom styling overriding `#footer` | Use standard `{{ print_footer(footer) }}` macro and verify `common_styles()` is loaded. |
| Table rows split or overlap across page breaks | Missing `page-break-inside` CSS rules | Ensure `{{ common_styles() }}` is invoked; it applies `page-break-inside: auto` on tables and `avoid` on `tr`. |
| German translation not rendered | String missing from `de.csv` or cache not cleared | Append `"English Source","Deutsche Übersetzung",` to `apps/becharged/becharged/translations/de.csv` and run `bench clear-cache`. |

---

## Completion Criteria

The print format development task is complete when:

- [ ] Print format template is created/updated in `print_format/<format_name>/<format_name>.html`
- [ ] Template begins with `common_styles()` and imports macros from `becharged/becharged/print_format/includes/print_macros.html`
- [ ] Layout conforms to DIN 5008: `#header`, `.contact-row` (`recipient_address` + `contact_info`), `{{ fold_marks() }}`, `#text`, and `{{ print_footer(footer) }}`
- [ ] All user-facing strings are wrapped in `_("...")`
- [ ] All new translation strings are added to `apps/becharged/becharged/translations/de.csv`
- [ ] Quantities, rates, totals, and dates are formatted using Frappe formatters
- [ ] Jinja syntax is validated with no unmatched tags or undefined variable errors

---

## Reference Examples in Codebase

- **Quotation (`bch_angebot`):** Grouped items, alternative positions, validity dates.
- **Sales Invoice (`bch_rechnung`):** Item separators, tax breakdown, SEPA mandate reference, monthly consumption attachment.
- **Delivery Note (`bch_lieferschein`):** Simple quantity table, shipping address resolution.
- **Purchase Order (`bch_einkausauftrag`):** Supplier address mapping, scheduled delivery date.
- **Dunning (`bch_mahnung`):** Overdue invoice list, dunning levels, dunning fees, interest.
- **Credit Note (`bch_gutschrift`, `bch_einkaufsrechnung`):** Billing periods, reverse charge notes.
