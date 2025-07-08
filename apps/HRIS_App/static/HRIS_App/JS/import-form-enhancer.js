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
            
            // Add visual indicator to label if not already present
            if (!label.querySelector('.required-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'required-indicator';
                indicator.textContent = ' *';
                indicator.style.color = '#ef4444';
                indicator.style.fontWeight = '700';
                label.appendChild(indicator);
            }
        } else {
            // Add optional field styling
            row.classList.add('optional-field');
            row.classList.add('optional-field-bg');
            
            // Add visual indicator to label if not already present
            if (!label.querySelector('.optional-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'optional-indicator';
                indicator.textContent = ' (optional)';
                indicator.style.color = '#6b7280';
                indicator.style.fontStyle = 'italic';
                indicator.style.fontSize = '0.9em';
                label.appendChild(indicator);
            }
        }
        
        // Add tooltip with field description if available
        const description = input.getAttribute('data-description') || getDefaultDescription(input.name);
        if (description) {
            addTooltip(label, description);
        }
    });}
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
    
    // Add a small note about required fields in import files
    if (form.classList.contains('import-form')) {
        const note = document.createElement('div');
        note.className = 'import-field-note';
        note.innerHTML = `<p><strong>Note:</strong> Required fields must have values in your import file. Optional fields can be left blank.</p>`;
        note.style.marginBottom = '15px';
        note.style.fontSize = '14px';
        note.style.color = '#4b5563';
        note.style.padding = '8px 12px';
        note.style.backgroundColor = '#f9fafb';
        note.style.borderRadius = '4px';
        note.style.borderLeft = '3px solid #3b82f6';
        
        form.insertBefore(note, form.querySelector('.import-field-legend').nextSibling);
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
            <li>Hover over field labels with <span style="font-weight: bold;">?</span> icon for detailed information about each field.</li>
            <li>Your import file <strong>must have column headers</strong> that exactly match the field names shown here.</li>
            <li>Date fields should be in YYYY-MM-DD format (e.g., 2023-12-31).</li>
            <li>For fields that accept multiple values (like qualifications), use commas to separate items.</li>
            <li>If you're unsure about required formats, download a sample template first.</li>
        </ul>
    `;
    
    // Insert at the beginning of the form
    form.insertBefore(instructions, form.firstChild);
    
    // Add a sample template download link if it doesn't exist
    if (!form.querySelector('.sample-template-link')) {
        const templateLinkContainer = document.createElement('div');
        templateLinkContainer.className = 'sample-template-container';
        templateLinkContainer.style.marginBottom = '20px';
        templateLinkContainer.style.textAlign = 'right';
        
        const templateLink = document.createElement('a');
        templateLink.className = 'sample-template-link';
        templateLink.href = '#'; // This should be updated to point to an actual template
        templateLink.textContent = 'Download Sample Template';
        templateLink.style.color = '#3b82f6';
        templateLink.style.textDecoration = 'none';
        templateLink.style.fontWeight = '500';
        templateLink.style.display = 'inline-flex';
        templateLink.style.alignItems = 'center';
        templateLink.style.gap = '5px';
        
        // Add download icon
        templateLink.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> Download Sample Template`;
        
        // Add click event to show a message if the template doesn't exist yet
        templateLink.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                alert('Sample template will be available soon. Please check back later.');
            }
        });
        
        templateLinkContainer.appendChild(templateLink);
        form.insertBefore(templateLinkContainer, form.querySelector('.import-instructions').nextSibling);
    }
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
        // Import form fields
        'file': 'Upload your CSV, XLS, or XLSX file containing the data to import. File must have headers matching the field names.',
        'format': 'Select the format of your import file (CSV, Excel XLS, or Excel XLSX).',
        'import_id': 'A unique identifier for this import batch for tracking purposes.',
        
        // Employee fields
        'SAP_ID': 'Unique SAP ID for the employee. This must be unique across all employees.',
        'email': 'Employee email address (must be unique). Used for system login and communications.',
        'name': 'Full name of the employee as it should appear in official documents.',
        'first_name': 'Employee\'s first name.',
        'last_name': 'Employee\'s last name or surname.',
        'designation': 'Job title or position of the employee within the organization.',
        'cadre': 'Employee cadre or category that determines benefits and career path.',
        'employee_type': 'Type of employment (e.g., permanent, contract, probation, temporary).',
        'employee_grade': 'Grade level of the employee that determines salary scale.',
        'branch': 'Branch code where the employee is assigned. Must match an existing branch in the system.',
        'region': 'Region name where the employee is located. Must match an existing region in the system.',
        'department': 'Department the employee belongs to within the organization.',
        'division': 'Division within the department where the employee works.',
        'qualifications': 'Comma-separated list of educational qualifications and certifications.',
        'date_of_joining': 'Date when the employee joined the organization (format: YYYY-MM-DD).',
        'date_of_birth': 'Employee\'s date of birth (format: YYYY-MM-DD).',
        'mobile_number': 'Employee mobile contact number. Include country code if applicable.',
        'phone_number': 'Employee\'s office phone number or extension.',
        'date_of_retirement': 'Expected retirement date of the employee (format: YYYY-MM-DD).',
        'remarks': 'Any additional notes or comments about the employee.',
        'grade_assignment': 'Performance grade assigned to the employee (e.g., A, B, C, D).',
        'status': 'Current employment status (e.g., active, inactive, on leave, terminated).',
        'gender': 'Employee\'s gender (e.g., Male, Female, Other).',
        'marital_status': 'Employee\'s marital status (e.g., Single, Married, Divorced, Widowed).',
        'address': 'Employee\'s residential address.',
        'emergency_contact': 'Name and contact information for emergency situations.',
        'reporting_manager': 'Name or ID of the employee\'s direct supervisor or manager.',
        'salary': 'Employee\'s base salary amount.',
        'contract_end_date': 'End date for contract employees (format: YYYY-MM-DD).',
        'probation_end_date': 'End date of probation period for new employees (format: YYYY-MM-DD).',
    };
    
    return descriptions[fieldName] || '';
}