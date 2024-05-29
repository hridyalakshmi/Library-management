// Copyright (c) 2024, hridya and contributors
// For license information, please see license.txt

frappe.query_reports["Article Report"] = {
	"filters": [
		{
			"fieldname": "article_name",
      "label": __("Article Name"),
      "fieldtype": "Link",
			"options": "Article",
			"width": 300
		},
		{
			"fieldname": "author",
      "label": __("Author"),
      "fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "publisher",
      "label": __("Publisher"),
      "fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "isbn",
			"label": __("ISBN"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "status",
      "label": __("Status"),
      "fieldtype": "Data",
			"width": 150

		}

	]
};
