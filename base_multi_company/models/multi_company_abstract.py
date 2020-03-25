# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MultiCompanyAbstract(models.AbstractModel):

    _name = "multi.company.abstract"
    _description = "Multi-Company Abstract"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        compute="_compute_company_id_and_visibility",
        inverse="_inverse_company_id",
        search="_search_company_id",
    )
    company_ids = fields.Many2many(
        string="Companies",
        comodel_name="res.company.assignment",
        auto_join=True,
        default=lambda self: self._default_company_ids(),
    )
    visible_for_all_companies = fields.Boolean(
        compute="_compute_company_id_and_visibility", store=True, index=True,
    )

    def _default_company_ids(self):
        return self.browse(self.env.company.ids)

    @api.depends("company_ids")
    def _compute_company_id_and_visibility(self):
        current_company = self.env.company
        for record in self:
            # Give the priority of the current company  to avoid access right
            # error
            if current_company.id in record.company_ids.ids:
                record.company_id = current_company.id
            else:
                record.company_id = record.company_ids[:1].id
            if not record.company_ids:
                record.visible_for_all_companies = True
            else:
                record.visible_for_all_companies = False

    def _inverse_company_id(self):
        for record in self:
            # Checking id not falsy due to bad data that can put '' in id
            if record.company_id.id:
                if record.company_id.id not in record.company_ids.ids:
                    record.company_ids = [(4, record.company_id.id)]
            else:
                # Empty the list of allowed companies (so it means all
                # companies are allowed) as it's the equivalent
                record.company_ids = [(5,)]

    def _search_company_id(self, operator, value):
        return [("company_ids", operator, value)]
