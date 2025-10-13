import pandas as pd
from io import BytesIO

# SOW EVALUATION SCHEMA DATA
sow_data = {
    'Section': [],
    'Requirement': [],
    'Standard Points': [],
    'Bonus Points': [],
    'Total Points': [],
    'Notes/Details': []
}

# SOW - General Requirements
sow_data['Section'].extend(['1.0 GENERAL REQUIREMENTS'] * 10)
sow_data['Requirement'].extend([
    '1.1 Understanding of Requirements',
    '1.2 Adequacy of Proposed Solution',
    '1.3 Compliance with Mandatory Dates',
    '1.4 Project Organization Structure',
    '1.5 Quality Assurance Approach',
    '1.6 Risk Management Strategy',
    '1.7 Communication Plan',
    '1.8 Resource Allocation',
    '1.9 Contingency Planning',
    'Subtotal General Requirements'
])
sow_data['Standard Points'].extend([5, 5, 10, 5, 5, 5, 5, 3, 2, 45])
sow_data['Bonus Points'].extend([0, 0, 0, 1, 1, 1, 1, 1, 0, 5])
sow_data['Total Points'].extend([5, 5, 10, 6, 6, 6, 6, 4, 2, 50])
sow_data['Notes/Details'].extend([
    'Clear demonstration of RFP understanding',
    'Solution addresses all requirements',
    'Critical: Budget prep by 1 Jul 2026, Go-live 1 Jan 2027',
    'Clear roles and responsibilities',
    'Testing, validation procedures',
    'Risk identification and mitigation',
    'Stakeholder communication approach',
    'Adequate staffing plan',
    'Backup plans for critical issues',
    ''
])

# SOW - Part I: Statement of Work Details
sow_sections = [
    ('2.0 PROJECT PLANNING & MANAGEMENT', [
        '2.1 Project Plan Development',
        '2.2 Quality Management',
        '2.3 Project Monitoring & Control',
        '2.4 Documentation Standards'
    ], [8, 6, 6, 5], [2, 2, 1, 0]),
    
    ('3.0 SYSTEM DEVELOPMENT', [
        '3.1 Solution Design',
        '3.2 System Configuration',
        '3.3 Customization Approach',
        '3.4 Integration Strategy'
    ], [10, 10, 8, 8], [2, 2, 2, 2]),
    
    ('4.0 DATA MIGRATION', [
        '4.1 Data Migration Strategy',
        '4.2 Data Cleansing Plan',
        '4.3 Migration Testing',
        '4.4 Validation Procedures'
    ], [8, 7, 6, 5], [2, 1, 1, 1]),
    
    ('5.0 TRAINING & CAPACITY BUILDING', [
        '5.1 Training Needs Assessment',
        '5.2 Training Materials',
        '5.3 Training Delivery',
        '5.4 Knowledge Transfer'
    ], [6, 6, 8, 6], [1, 1, 2, 1]),
    
    ('6.0 TESTING & ACCEPTANCE', [
        '6.1 Test Strategy',
        '6.2 UAT Support',
        '6.3 Performance Testing',
        '6.4 Acceptance Criteria'
    ], [7, 7, 6, 5], [1, 1, 1, 0]),
    
    ('7.0 DEPLOYMENT & GO-LIVE', [
        '7.1 Deployment Plan',
        '7.2 Rollout Strategy',
        '7.3 Go-Live Support',
        '7.4 Post-Implementation Support'
    ], [8, 7, 6, 5], [2, 1, 1, 1]),
    
    ('8.0 WARRANTY & MAINTENANCE', [
        '8.1 Warranty Period Support',
        '8.2 Defect Resolution',
        '8.3 System Updates',
        '8.4 Technical Support'
    ], [6, 5, 4, 5], [1, 1, 0, 1])
]

for section_title, requirements, std_points, bonus_points in sow_sections:
    section_total_std = sum(std_points)
    section_total_bonus = sum(bonus_points)
    section_total = section_total_std + section_total_bonus
    
    sow_data['Section'].extend([section_title] * (len(requirements) + 1))
    sow_data['Requirement'].extend(requirements + [f'Subtotal {section_title}'])
    sow_data['Standard Points'].extend(std_points + [section_total_std])
    sow_data['Bonus Points'].extend(bonus_points + [section_total_bonus])
    sow_data['Total Points'].extend([s+b for s, b in zip(std_points, bonus_points)] + [section_total])
    sow_data['Notes/Details'].extend([''] * (len(requirements) + 1))

# Grand Total for SOW
sow_data['Section'].append('GRAND TOTAL - SOW')
sow_data['Requirement'].append('Total Statement of Work')
sow_data['Standard Points'].append(130)
sow_data['Bonus Points'].append(20)
sow_data['Total Points'].append(150)
sow_data['Notes/Details'].append('Minimum score: 75 points')

# Create SOW DataFrame
df_sow = pd.DataFrame(sow_data)

# TOM EVALUATION SCHEMA DATA
tom_data = {
    'Section': [],
    'Functional Area': [],
    'Requirement': [],
    'Standard Points': [],
    'Bonus Points': [],
    'Total Points': [],
    'Priority': []
}

# TOM Major Sections
tom_sections = [
    ('1.0 BUDGET PREPARATION', [
        ('1.1 Budget Classification', ['Budget structure setup', 'Economic classification', 'Functional classification', 'Administrative classification'], [8, 6, 6, 5], [2, 1, 1, 1]),
        ('1.2 Budget Formulation', ['Bottom-up budgeting', 'Budget ceilings', 'Multi-year budgeting', 'Budget justification'], [8, 7, 7, 6], [2, 1, 1, 1]),
        ('1.3 Budget Analysis', ['Budget reports', 'Variance analysis', 'Budget forecasting'], [6, 6, 5], [1, 1, 1])
    ]),
    
    ('2.0 BUDGET EXECUTION', [
        ('2.1 Commitment Management', ['Purchase requisitions', 'Purchase orders', 'Commitment tracking', 'Encumbrance control'], [8, 8, 7, 6], [2, 2, 1, 1]),
        ('2.2 Payment Processing', ['Payment authorization', 'Payment scheduling', 'Payment execution', 'Payment tracking'], [8, 7, 8, 6], [2, 1, 2, 1]),
        ('2.3 Cash Management', ['Cash forecasting', 'Cash allocation', 'Bank reconciliation'], [7, 6, 7], [1, 1, 2])
    ]),
    
    ('3.0 ACCOUNTING & FINANCIAL REPORTING', [
        ('3.1 General Ledger', ['Chart of accounts', 'Double-entry accounting', 'Journal entries', 'Period-end closing'], [10, 8, 7, 7], [2, 2, 1, 1]),
        ('3.2 Financial Reporting', ['Budget execution reports', 'Financial statements', 'IPSAS compliance', 'GFSM 2014 compliance'], [8, 8, 10, 8], [2, 2, 3, 2]),
        ('3.3 Asset Management', ['Asset register', 'Depreciation', 'Asset tracking'], [6, 6, 5], [1, 1, 1])
    ]),
    
    ('4.0 REVENUE MANAGEMENT', [
        ('4.1 Revenue Collection', ['Revenue classification', 'Revenue tracking', 'Receipt management'], [7, 7, 6], [1, 1, 1]),
        ('4.2 Tax Administration', ['Tax assessment', 'Tax collection', 'Tax reporting'], [6, 6, 5], [1, 1, 0])
    ]),
    
    ('5.0 DEBT MANAGEMENT', [
        ('5.1 Loan Tracking', ['Loan register', 'Disbursement tracking', 'Repayment scheduling'], [6, 6, 6], [1, 1, 1]),
        ('5.2 Debt Reporting', ['Debt portfolio reports', 'Debt service reports'], [6, 5], [1, 1])
    ]),
    
    ('6.0 PAYROLL INTEGRATION', [
        ('6.1 Payroll Interface', ['Payroll data import', 'Payroll posting', 'Payroll reconciliation'], [7, 7, 6], [1, 1, 1])
    ]),
    
    ('7.0 SYSTEM ADMINISTRATION', [
        ('7.1 User Management', ['User roles', 'Access control', 'Audit trails'], [7, 8, 8], [1, 2, 2]),
        ('7.2 System Configuration', ['Parameter setup', 'Workflow configuration', 'Report customization'], [6, 7, 6], [1, 1, 1]),
        ('7.3 Data Security', ['Data encryption', 'Backup & recovery', 'Cybersecurity measures'], [8, 7, 10], [2, 1, 3])
    ]),
    
    ('8.0 INTEGRATION & INTEROPERABILITY', [
        ('8.1 System Integration', ['Banking system integration', 'HR/Payroll integration', 'Revenue system integration'], [8, 7, 7], [2, 1, 1]),
        ('8.2 Data Exchange', ['API capabilities', 'Data import/export', 'Real-time interfaces'], [7, 6, 7], [1, 1, 1])
    ]),
    
    ('9.0 REPORTING & ANALYTICS', [
        ('9.1 Standard Reports', ['Pre-configured reports', 'Ad-hoc reporting', 'Dashboard functionality'], [7, 7, 8], [1, 1, 2]),
        ('9.2 Business Intelligence', ['Data analytics', 'Trend analysis', 'Predictive analytics'], [6, 6, 5], [1, 1, 2])
    ])
]

priority_map = {
    'Budget': 'Critical',
    'Payment': 'Critical',
    'Accounting': 'Critical',
    'Reporting': 'Critical',
    'Security': 'Critical',
    'User': 'High',
    'Integration': 'High',
    'Revenue': 'Medium',
    'Debt': 'Medium',
    'Asset': 'Medium'
}

for section_title, functional_areas in tom_sections:
    for func_area, requirements, std_points, bonus_points in functional_areas:
        for i, req in enumerate(requirements):
            tom_data['Section'].append(section_title)
            tom_data['Functional Area'].append(func_area)
            tom_data['Requirement'].append(req)
            tom_data['Standard Points'].append(std_points[i])
            tom_data['Bonus Points'].append(bonus_points[i])
            tom_data['Total Points'].append(std_points[i] + bonus_points[i])
            
            # Assign priority
            priority = 'Medium'
            for key, val in priority_map.items():
                if key in func_area or key in req:
                    priority = val
                    break
            tom_data['Priority'].append(priority)
        
        # Subtotal for functional area
        tom_data['Section'].append(section_title)
        tom_data['Functional Area'].append(f'Subtotal - {func_area}')
        tom_data['Requirement'].append('')
        tom_data['Standard Points'].append(sum(std_points))
        tom_data['Bonus Points'].append(sum(bonus_points))
        tom_data['Total Points'].append(sum(std_points) + sum(bonus_points))
        tom_data['Priority'].append('')

# Grand Total for TOM
tom_data['Section'].append('GRAND TOTAL - TOM')
tom_data['Functional Area'].append('Total Target Operating Model')
tom_data['Requirement'].append('')
tom_data['Standard Points'].append(420)
tom_data['Bonus Points'].append(30)
tom_data['Total Points'].append(450)
tom_data['Priority'].append('')
tom_data['Section'].append('OVERALL MINIMUM')
tom_data['Functional Area'].append('Minimum Responsive Score')
tom_data['Requirement'].append('')
tom_data['Standard Points'].append(350)
tom_data['Bonus Points'].append(0)
tom_data['Total Points'].append(350)
tom_data['Priority'].append('Critical')

# Create TOM DataFrame
df_tom = pd.DataFrame(tom_data)

# Create Excel files
sow_output = BytesIO()
tom_output = BytesIO()

with pd.ExcelWriter(sow_output, engine='xlsxwriter') as writer:
    df_sow.to_excel(writer, sheet_name='SOW Evaluation Schema', index=False)
    
    workbook = writer.book
    worksheet = writer.sheets['SOW Evaluation Schema']
    
    # Format headers
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    
    # Format subtotals
    subtotal_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    # Format grand total
    total_format = workbook.add_format({
        'bold': True,
        'bg_color': '#FFC000',
        'border': 1
    })
    
    # Set column widths
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:E', 15)
    worksheet.set_column('F:F', 50)
    
    # Write headers
    for col_num, value in enumerate(df_sow.columns.values):
        worksheet.write(0, col_num, value, header_format)

with pd.ExcelWriter(tom_output, engine='xlsxwriter') as writer:
    df_tom.to_excel(writer, sheet_name='TOM Evaluation Schema', index=False)
    
    workbook = writer.book
    worksheet = writer.sheets['TOM Evaluation Schema']
    
    # Format headers
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#70AD47',
        'font_color': 'white',
        'border': 1
    })
    
    # Set column widths
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 35)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:F', 15)
    worksheet.set_column('G:G', 12)
    
    # Write headers
    for col_num, value in enumerate(df_tom.columns.values):
        worksheet.write(0, col_num, value, header_format)

print("Excel files created successfully!")
print(f"\nSOW Evaluation Schema: {len(df_sow)} rows")
print(f"TOM Evaluation Schema: {len(df_tom)} rows")
print("\nNote: Download functionality requires file system access.")
print("The data structures are ready for Excel export.")