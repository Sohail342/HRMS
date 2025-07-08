/**
 * Custom JavaScript for Unfold Admin Panel
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancements
    initSidebarToggle();
    initCardAnimations();
    initFormEnhancements();
    initTableEnhancements();
    initTooltips();
    initTabSwitching();
    initCollapsibleSections();
    initDarkModeToggle();
});

/**
 * Sidebar toggle functionality for mobile views
 */
function initSidebarToggle() {
    const sidebarToggle = document.querySelector('.unfold-sidebar-toggle');
    const sidebar = document.querySelector('.unfold-sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('unfold-sidebar-expanded');
            document.body.classList.toggle('unfold-sidebar-open');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth < 768 && 
                document.body.classList.contains('unfold-sidebar-open') && 
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('unfold-sidebar-expanded');
                document.body.classList.remove('unfold-sidebar-open');
            }
        });
    }
}

/**
 * Card animations and interactions
 */
function initCardAnimations() {
    const cards = document.querySelectorAll('.unfold-card');
    
    cards.forEach(card => {
        // Add entrance animation class
        card.classList.add('unfold-fade-in');
        
        // Add hover effect for cards with actions
        const cardActions = card.querySelector('.unfold-card-actions');
        if (cardActions) {
            card.addEventListener('mouseenter', function() {
                cardActions.style.opacity = '1';
            });
            
            card.addEventListener('mouseleave', function() {
                cardActions.style.opacity = '0.2';
            });
        }
    });
}

/**
 * Form field enhancements
 */
function initFormEnhancements() {
    // Enhance form controls
    const formControls = document.querySelectorAll('.unfold-form-control, input, select, textarea');
    
    formControls.forEach(control => {
        // Add focus animation
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('unfold-input-focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('unfold-input-focused');
        });
        
        // Add floating labels effect
        if (control.tagName.toLowerCase() !== 'select') {
            control.addEventListener('input', function() {
                if (this.value) {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
            
            // Initialize state on page load
            if (control.value) {
                control.classList.add('has-value');
            }
        }
        
        // Add required/optional field styling
        if (control.required || control.getAttribute('data-required') === 'true') {
            control.parentElement.classList.add('required-field');
            control.parentElement.classList.add('mandatory-field-bg');
        } else {
            control.parentElement.classList.add('optional-field');
            control.parentElement.classList.add('optional-field-bg');
        }
        
        // Add tooltip for field description if available
        const description = control.getAttribute('data-description');
        if (description) {
            const label = control.parentElement.querySelector('label');
            if (label) {
                addFieldTooltip(label, description);
            }
        }
    });
    
    // Add field legend to all forms
    addFieldLegendToForms();
}

/**
 * Add tooltip to field label
 */
function addFieldTooltip(element, description) {
    // Check if tooltip already exists
    if (element.querySelector('.field-tooltip')) return;
    
    const tooltip = document.createElement('span');
    tooltip.className = 'field-tooltip';
    tooltip.innerHTML = `
        <span class="tooltip-icon">?</span>
        <span class="tooltip-text">${description}</span>
    `;
    
    element.appendChild(tooltip);
}

/**
 * Add field legend to all forms
 */
function addFieldLegendToForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip if legend already exists or if it's a search form
        if (form.querySelector('.field-legend') || form.classList.contains('search-form')) return;
        
        const legend = document.createElement('div');
        legend.className = 'import-field-legend field-legend';
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
    });
}
}

/**
 * Table enhancements
 */
function initTableEnhancements() {
    const tables = document.querySelectorAll('.unfold-table');
    
    tables.forEach(table => {
        // Add row highlighting on hover
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.classList.add('unfold-row-highlight');
            });
            
            row.addEventListener('mouseleave', function() {
                this.classList.remove('unfold-row-highlight');
            });
        });
        
        // Add sortable columns if table has the sortable class
        if (table.classList.contains('sortable')) {
            const headers = table.querySelectorAll('th');
            headers.forEach(header => {
                if (!header.classList.contains('no-sort')) {
                    header.classList.add('unfold-sortable');
                    header.addEventListener('click', function() {
                        sortTable(table, Array.from(headers).indexOf(this));
                    });
                }
            });
        }
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'unfold-tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            tooltip.style.opacity = '1';
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
}

/**
 * Tab switching functionality
 */
function initTabSwitching() {
    const tabContainers = document.querySelectorAll('.unfold-tabs');
    
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.unfold-tab');
        const tabContents = container.querySelectorAll('.unfold-tab-content');
        
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to current tab and content
                this.classList.add('active');
                tabContents[index].classList.add('active');
            });
        });
    });
}

/**
 * Collapsible sections
 */
function initCollapsibleSections() {
    const collapsibles = document.querySelectorAll('.unfold-collapsible');
    
    collapsibles.forEach(collapsible => {
        const header = collapsible.querySelector('.unfold-collapsible-header');
        const content = collapsible.querySelector('.unfold-collapsible-content');
        
        if (header && content) {
            header.addEventListener('click', function() {
                collapsible.classList.toggle('expanded');
                
                if (collapsible.classList.contains('expanded')) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                } else {
                    content.style.maxHeight = '0';
                }
            });
            
            // Initialize state
            if (collapsible.classList.contains('expanded')) {
                content.style.maxHeight = content.scrollHeight + 'px';
            } else {
                content.style.maxHeight = '0';
            }
        }
    });
}

/**
 * Dark mode toggle
 */
function initDarkModeToggle() {
    const darkModeToggle = document.querySelector('.unfold-dark-mode-toggle');
    
    if (darkModeToggle) {
        // Check for saved user preference
        const darkModePreference = localStorage.getItem('unfoldDarkMode');
        if (darkModePreference === 'true') {
            document.body.classList.add('unfold-dark-mode');
            darkModeToggle.classList.add('active');
        }
        
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('unfold-dark-mode');
            this.classList.toggle('active');
            
            // Save user preference
            localStorage.setItem('unfoldDarkMode', document.body.classList.contains('unfold-dark-mode'));
        });
    }
}

/**
 * Helper function to sort tables
 */
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const headers = table.querySelectorAll('th');
    const header = headers[columnIndex];
    
    // Toggle sort direction
    const isAscending = !header.classList.contains('sort-asc');
    
    // Remove sort classes from all headers
    headers.forEach(h => {
        h.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add sort class to current header
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Sort as strings
        return isAscending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });
    
    // Reappend rows in new order
    rows.forEach(row => tbody.appendChild(row));
}