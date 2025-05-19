/**
 * Form Field Enhancer
 * 
 * This script enhances all forms UI by:
 * 1. Adding visual indicators for required and optional fields
 * 2. Adding tooltips with field descriptions
 * 3. Adding a legend explaining the field indicators
 */

document.addEventListener('DOMContentLoaded', function() {
    enhanceAllForms();
});

function enhanceAllForms() {
    // Enhance import forms
    enhanceImportForm();
    
    // Enhance all other forms
    enhanceRegularForms();
}

function enhanceRegularForms() {
    // Get all form rows in regular forms
    const formRows = document.querySelectorAll('form .form-row, form .fieldBox, form .aligned');
    if (formRows.length === 0) return;
    
    // Add a legend to each form
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip if it's an import form (already handled) or a search form
        if (form.classList.contains('import-form') || form.classList.contains('search-form')) return;
        
        addFieldLegend(form);
    });
    
    // Process each form row
    formRows.forEach(row => {
        const input = row.querySelector('input, select, textarea');
        const label = row.querySelector('label');
        
        if (!input || !label) return;
        
        // Check if the field is required
        const isRequired = input.required || input.getAttribute('data-required') === 'true';
        
        if (isRequired) {
            // Add required field styling
            row.classList.add('required-field');
            row.classList.add('mandatory-field-bg');
        } else {
            // Add optional field styling
            row.classList.add('optional-field');
            row.classList.add('optional-field-bg');
        }
        
        // Add tooltip with field description if available
        const description = input.getAttribute('data-description') || getDefaultDescription(input.name);
        if (description) {
            addTooltip(label, description);
        }
    });
}

function enhanceImportForm() {
    // Get all form rows in the import form
    const formRows = document.querySelectorAll('.import-form .form-row');
    if (formRows.length === 0) return;
    
    // Add a legend at the top of the form
    addFieldLegend(document.querySelector('.import-form'));
    
    // Add instructions
    addImportInstructions();
    
    // Process each form row
    formRows.forEach(row => {
        const input = row.querySelector('input, select, textarea');
        const label = row.querySelector('label');
        
        if (!input || !label) return;
        
        // Check if the field is required
        const isRequired = input.required || input.getAttribute('data-required') === 'true';
        
        if (isRequired) {
            // Add required field styling
            row.classList.add('required-field');
            row.classList.add('mandatory-field-bg');
        } else {
            // Add optional field styling
            row.classList.add('optional-field');
            row.classList.add('optional-field-bg');
        }
        
        // Add tooltip with field description if available
        const description = input.getAttribute('data-description') || getDefaultDescription(input.name);
        if (description) {
            addTooltip(label, description);
        }
    });
}

function addFieldLegend(form) {
    if (!form) return;
    
    // Skip if legend already exists
    if (form.querySelector('.import-field-legend')) return;
    
    const legend = document.createElement('div');
    legend.className = 'import-field-legend';
    legend.innerHTML = `
        <div class="legend-item">
            <span class="legend-mandatory">*</span>
            <span>Required field</span>
        </div>
        <div class="legend-item">
            <span class="legend-optional">(optional)</span>
            <span>Optional field</span>
        </div>
    `;
    
    // Insert at the beginning of the form
    if (form.firstChild) {
        form.insertBefore(legend, form.firstChild);
    } else {
        form.appendChild(legend);
    }
}

function addImportInstructions() {
    const form = document.querySelector('.import-form');
    if (!form) return;
    
    const instructions = document.createElement('div');
    instructions.className = 'import-instructions';
    instructions.innerHTML = `
        <h3>Import Instructions</h3>
        <ul>
            <li>Fields marked with <span class="legend-mandatory">*</span> are mandatory and must be included in your import file.</li>
            <li>Fields marked as <span class="legend-optional">(optional)</span> can be left blank.</li>
            <li>Hover over field labels with <span style="font-weight: bold;">?</span> icon for more information.</li>
            <li>Make sure your CSV/Excel file has headers that match the field names.</li>
        </ul>
    `;
    
    // Insert at the beginning of the form
    form.insertBefore(instructions, form.firstChild);
}

function addTooltip(element, description) {
    const tooltip = document.createElement('span');
    tooltip.className = 'field-tooltip';
    tooltip.innerHTML = `
        <span class="tooltip-icon">?</span>
        <span class="tooltip-text">${description}</span>
    `;
    
    element.appendChild(tooltip);
}

function getDefaultDescription(fieldName) {
    // Default descriptions for common fields
    const descriptions = {
        'file': 'Upload your CSV, XLS, or XLSX file containing the data to import.',
        'format': 'Select the format of your import file.',
        'import_id': 'A unique identifier for this import.',
        'SAP_ID': 'Unique SAP ID for the employee.',
        'email': 'Employee email address (must be unique).',
        'name': 'Full name of the employee.',
        'designation': 'Job title or position of the employee.',
        'cadre': 'Employee cadre or category.',
        'employee_type': 'Type of employment (e.g., permanent, contract).',
        'employee_grade': 'Grade level of the employee.',
        'branch': 'Branch code where the employee is assigned.',
        'region': 'Region name where the employee is located.',
        'qualifications': 'Comma-separated list of qualifications.',
        'date_of_joining': 'Date when the employee joined the organization.',
        'mobile_number': 'Employee mobile contact number.',
        'date_of_retirement': 'Expected retirement date of the employee.',
        'remarks': 'Any additional notes or comments about the employee.',
        'grade_assignment': 'Performance grade assigned to the employee.',
    };
    
    return descriptions[fieldName] || '';
}