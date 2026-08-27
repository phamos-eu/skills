# Print Macros Reference

Complete reference for all macros in `becharged/becharged/print_format/includes/print_macros.html`.

## Jinja Import Statement

All print formats in becharged import macros using:

```jinja
{%- from "becharged/becharged/print_format/includes/print_macros.html" 
    import common_styles, print_header, recipient_address, customer_address, 
    contact_info, salutation, print_footer, fold_marks -%}
```

---

## `common_styles()`

**Purpose:** Provides base CSS for all print formats, including margins, header/logo alignment, DIN 5008 fold marks, table page-breaks, and footer styling.

**Signature:**
```jinja
{% macro common_styles() %}
```

**Includes:**
- `.print-format` container styling (margins: top 10mm, bottom 20mm, font-size: 8pt)
- `#header` (35mm height, right-aligned) & `#logo` (25mm height, absolute position)
- `.contact-row` (relative, height 65mm, width 180mm, left 15mm)
- `#sender` (17.7mm height) & `#address` (95mm width, float left)
- `#contact` (85mm width, float right, table padding 1.5px)
- `#subject` (height 5mm, bold)
- DIN 5008 fold and punch marks: `#faltmarke-1` (115mm), `#lochmarke` (158.5mm), `#faltmarke-2` (220mm)
- `#text` (margin-top 5mm, margin-left 20mm, margin-right 15mm)
- Table rules: `page-break-inside: auto;`, `tr { page-break-inside: avoid; }`, `thead { display: table-header-group; }`
- `#footer` (margin-left 20mm, padding-right 20mm, margin-top 10mm, position: static, bottom: 0)

**Usage:**
```jinja
{{ common_styles() }}
```

---

## `print_header(letter_head=None, no_letterhead=False)`

**Purpose:** Renders the document header with the official becharged logo or a custom letterhead.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `letter_head` | HTML / string | `None` | Custom letterhead HTML content |
| `no_letterhead` | boolean | `False` | When True, suppresses letterhead and renders default logo |

**Behavior:**
- If `letter_head` is provided and `no_letterhead` is `False`, renders `letter_head`.
- Otherwise renders default logo: `/assets/becharged/png/customcolor_logo_transparent_background-150.png` inside `#header`.

**Usage:**
```jinja
<!-- Default logo -->
{{ print_header() }}

<!-- With letterhead variable from print context -->
{{ print_header(letter_head, no_letterhead) }}
```

---

## `sender_address()`

**Purpose:** Renders the standard DIN 5008 sender reference line above the recipient address.

**Output:**
```html
<div id="sender">
    <p>becharged GmbH - Lupfenstraße 7 - 78609 Tuningen</p>
</div>
```

**Note:** Automatically invoked within `recipient_address()`. Rarely called standalone.

---

## `recipient_address(doc, contact=None, use_shipping=False, recipient_field="customer_name", show_contact=True)`

**Purpose:** Renders DIN 5008-compliant recipient address window with sender line, company/recipient name, contact person attention line, and full street/city/country address.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `doc` | Document | **required** | Frappe document object (e.g. Sales Invoice, Quotation) |
| `contact` | Contact doc / dict | `None` | Contact document for attention line |
| `use_shipping` | boolean | `False` | When True, uses `doc.shipping_address_name` if present |
| `recipient_field` | string | `"customer_name"` | Field on `doc` for recipient name (e.g., `"customer_name"`, `"supplier_name"`) |
| `show_contact` | boolean | `True` | Whether to render `Attn. <Contact Name>` |

**Behavior & Address Resolution:**
1. Calls `sender_address()`.
2. Evaluates recipient name from `doc[recipient_field]`.
3. Resolves Address doc using `doc.shipping_address_name` (if `use_shipping`), otherwise `doc.customer_address` or `doc.supplier_address`.
4. If `show_contact` and `contact` are present, outputs `Attn. <first_name> <last_name>` (translated via `_("Attn.")`).
5. Formats address lines: `address_line1`, `address_line2`, `pincode + city`, `country`.
6. Falls back to `doc.address_display` if Address doc is not resolved directly.

**Usage Examples:**
```jinja
<!-- Customer billing address with contact -->
{{ recipient_address(doc, contact) }}

<!-- Shipping address -->
{{ recipient_address(doc, contact, use_shipping=True) }}

<!-- Supplier purchase order address -->
{{ recipient_address(doc, contact, False, "supplier_name") }}
```

---

## `customer_address(doc, contact=None, use_shipping=False)`

**Purpose:** Convenience wrapper calling `recipient_address(doc, contact, use_shipping, "customer_name", True)`.

**Usage:**
```jinja
{{ customer_address(doc, contact) }}
{{ customer_address(doc, contact, use_shipping=True) }}
```

---

## `contact_info(doc, title, doc_label, date_field="posting_date", extra_rows=[])`

**Purpose:** Renders the right-hand document metadata block (title, document number, date, and custom key-value rows).

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `doc` | Document | **required** | Frappe document object |
| `title` | string | **required** | Document heading (translated with `_(title)`) |
| `doc_label` | string | **required** | Label for document number (translated with `_(doc_label)`) |
| `date_field` | string | `"posting_date"` | Field name on `doc` for the primary date |
| `extra_rows` | list of dicts | `[]` | Extra metadata rows `[{"label": "...", "value": "..."}]` |

**Standard Rows Rendered:**
1. **Title Row**: `<b>{{ _(title) }}</b>` (10pt font)
2. **Doc Number**: `{{ _(doc_label) }}:` -> `{{ doc.name }}`
3. **Date**: `{{ _("Date") }}:` -> `{{ frappe.utils.formatdate(doc[date_field], "dd. MMMM yyyy") }}`
4. **Extra Rows**: Iterates over `extra_rows` where `row.value` is non-empty, translating `_(row.label)`.

**Usage Example:**
```jinja
{% set extra_rows = [
    {"label": _("Customer number"), "value": doc.customer},
    {"label": _("Contact person"), "value": doc.custom_ansprechpartner if doc.custom_ansprechpartner else frappe.db.get_value("User", frappe.session.user, "full_name")},
    {"label": _("Email"), "value": frappe.db.get_value("User", frappe.session.user, "email")}
] %}
{{ contact_info(doc, _("INVOICE"), _("Receipt number"), "posting_date", extra_rows) }}
```

---

## `salutation(contact=None)`

**Purpose:** Renders German formal business salutation with gender-appropriate grammar.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `contact` | Contact doc / dict | `None` | Contact object containing `salutation` and `last_name` |

**Behavior:**
- If `contact` is missing or lacks `salutation`/`last_name`:
  `{{ _("Dear Sir or Madam") }},` -> German: *"Sehr geehrte Damen und Herren,"*
- If `contact` is present with male salutation ("Hr.", "Herr"):
  `{{ _("Dear") }}r {{ contact.salutation }} {{ contact.last_name }},` -> German: *"Sehr geehrter Herr <Name>,"*
- If `contact` is female ("Frau"):
  `{{ _("Dear") }} {{ contact.salutation }} {{ contact.last_name }},` -> German: *"Sehr geehrte Frau <Name>,"*

**Usage:**
```jinja
{% if doc.contact_person %}
    {% set contact = frappe.get_doc("Contact", doc.contact_person) %}
{% endif %}

{{ salutation(contact) }}
```

---

## `print_footer(footer_content)`

**Purpose:** Renders PDF-compatible letterhead footer.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `footer_content` | HTML / string | **required** | Footer HTML content (typically passed from ERPNext `footer` context variable) |

**Structure:**
```html
<div id="footer" class="visible-pdf">
    <div class="print-format-footer">
        {{ footer_content }}
    </div>
</div>
```

**Usage:**
```jinja
{{ print_footer(footer) }}
```

---

## `fold_marks()`

**Purpose:** Renders standard DIN 5008 fold marks and hole-punch mark on the left margin for standard DL/C6 window envelopes.

**Positions:**
- `faltmarke-1`: `115mm` from top
- `lochmarke`: `158.5mm` from top (center hole punch mark)
- `faltmarke-2`: `220mm` from top

**Structure:**
```html
<div id="faltmarke-1">-</div>
<div id="lochmarke">-</div>
<div id="faltmarke-2">-</div>
```

**Usage:**
```jinja
{{ fold_marks() }}
```

---

## Utility Classes in `common_styles()`

| Class | Purpose | Example |
|---|---|---|
| `.w-100` | Full width container / table (`width: 100%`) | `<table class="w-100">` |
| `.black-border` | Solid black 1px top and bottom border | `<thead class="black-border">` |
| `.text-right` | Right-aligned cell text (`text-align: right`) | `<td class="text-right">` |
| `.text-small` | 6pt fine print text | `<p class="text-small">` |
