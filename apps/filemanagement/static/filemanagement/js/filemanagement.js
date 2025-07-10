// File Management Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize file upload drag and drop functionality
    initFileUpload();
    
    // Initialize filter panel toggle
    initFilterPanel();
    
    // Initialize date range pickers
    initDatePickers();
    
    // Initialize delete confirmation
    initDeleteConfirmation();
});

/**
 * Initialize file upload drag and drop functionality
 */
function initFileUpload() {
    const fileUploadContainer = document.querySelector('.file-upload-container');
    const fileInput = document.querySelector('#file');
    
    if (!fileUploadContainer || !fileInput) return;
    
    // Update file name display when file is selected
    fileInput.addEventListener('change', function() {
        const fileNameDisplay = document.querySelector('.file-name-display');
        if (fileNameDisplay) {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
                fileNameDisplay.classList.remove('text-gray-500');
                fileNameDisplay.classList.add('text-gray-900', 'font-medium');
            } else {
                fileNameDisplay.textContent = 'No file selected';
                fileNameDisplay.classList.remove('text-gray-900', 'font-medium');
                fileNameDisplay.classList.add('text-gray-500');
            }
        }
    });
    
    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploadContainer.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploadContainer.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileUploadContainer.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        fileUploadContainer.classList.add('dragover');
    }
    
    function unhighlight() {
        fileUploadContainer.classList.remove('dragover');
    }
    
    fileUploadContainer.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        
        // Trigger change event
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
}

/**
 * Initialize filter panel toggle functionality
 */
function initFilterPanel() {
    const filterToggle = document.querySelector('.filter-toggle');
    const filterPanel = document.querySelector('.filter-panel-body');
    const filterIcon = document.querySelector('.filter-icon');
    
    if (!filterToggle || !filterPanel) return;
    
    filterToggle.addEventListener('click', function() {
        filterPanel.classList.toggle('expanded');
        
        if (filterIcon) {
            if (filterPanel.classList.contains('expanded')) {
                filterIcon.classList.remove('fa-chevron-down');
                filterIcon.classList.add('fa-chevron-up');
            } else {
                filterIcon.classList.remove('fa-chevron-up');
                filterIcon.classList.add('fa-chevron-down');
            }
        }
    });
    
    // Mobile filter toggle
    const mobileFilterToggle = document.querySelector('.mobile-filter-toggle');
    const filterPanelMobile = document.querySelector('.filter-panel');
    const closeFilterButton = document.querySelector('.close-filter-button');
    
    if (mobileFilterToggle && filterPanelMobile) {
        mobileFilterToggle.addEventListener('click', function() {
            filterPanelMobile.classList.add('active');
        });
    }
    
    if (closeFilterButton && filterPanelMobile) {
        closeFilterButton.addEventListener('click', function() {
            filterPanelMobile.classList.remove('active');
        });
    }
}

/**
 * Initialize date range pickers
 */
function initDatePickers() {
    // This function would initialize date pickers if using a library
    // For now, we'll use the browser's native date input
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set default values or initialize date picker library here if needed
    });
}

/**
 * Initialize delete confirmation
 */
function initDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('.delete-file-button');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Handle employee selection in file upload form
 */
function handleEmployeeSelection() {
    const employeeSelect = document.querySelector('#employee');
    const employeeInfoContainer = document.querySelector('#employee-info');
    
    if (!employeeSelect || !employeeInfoContainer) return;
    
    employeeSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const employeeId = selectedOption.value;
        
        if (employeeId) {
            // Fetch employee details via AJAX
            fetch(`/api/employee/${employeeId}/`)
                .then(response => response.json())
                .then(data => {
                    // Update employee info display
                    employeeInfoContainer.innerHTML = `
                        <div class="mt-4 bg-blue-50 p-4 rounded-md">
                            <h3 class="text-sm font-medium text-blue-800">Employee Information</h3>
                            <div class="mt-2 grid grid-cols-2 gap-2 text-sm">
                                <div>
                                    <span class="text-gray-500">SAP ID:</span>
                                    <span class="text-gray-900 ml-1">${data.sap_id}</span>
                                </div>
                                <div>
                                    <span class="text-gray-500">Designation:</span>
                                    <span class="text-gray-900 ml-1">${data.designation}</span>
                                </div>
                                <div>
                                    <span class="text-gray-500">Division:</span>
                                    <span class="text-gray-900 ml-1">${data.division}</span>
                                </div>
                                <div>
                                    <span class="text-gray-500">Branch:</span>
                                    <span class="text-gray-900 ml-1">${data.branch}</span>
                                </div>
                            </div>
                        </div>
                    `;
                    employeeInfoContainer.classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Error fetching employee data:', error);
                    employeeInfoContainer.innerHTML = `
                        <div class="mt-4 bg-red-50 p-4 rounded-md">
                            <p class="text-sm text-red-800">Error loading employee information. Please try again.</p>
                        </div>
                    `;
                    employeeInfoContainer.classList.remove('hidden');
                });
        } else {
            employeeInfoContainer.classList.add('hidden');
        }
    });
}