document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('pdf_file');
    const fileNameDisplay = document.getElementById('file-name-display');
    const fileName = document.getElementById('file-name');
    const selectedFileInfo = document.getElementById('selected-file-info');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Update the file name display
                fileName.textContent = file.name;
                fileNameDisplay.textContent = 'File selected';
                
                // Show the selected file info section
                selectedFileInfo.classList.remove('hidden');
                
                // Validate file type
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    selectedFileInfo.innerHTML = `
                        <div class="flex items-center p-2 bg-red-50 rounded-lg border border-red-100">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <span class="text-sm text-red-700 font-medium">Error: Only PDF files are allowed</span>
                        </div>
                    `;
                }
            } else {
                // Reset to default state if no file is selected
                fileNameDisplay.textContent = 'Click to select PDF file';
                selectedFileInfo.classList.add('hidden');
            }
        });
    }
});