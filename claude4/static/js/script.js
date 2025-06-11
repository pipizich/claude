document.addEventListener('DOMContentLoaded', function() {
    // Modals
    const addArtworkModal = document.getElementById('add-artwork-modal');
    const editArtworkModal = document.getElementById('edit-artwork-modal');
    const viewDescriptionModal = document.getElementById('view-description-modal');
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');
    
    // Buttons
    const addArtworkBtn = document.getElementById('add-artwork-btn');
    const editBtns = document.querySelectorAll('.btn-edit');
    const deleteBtns = document.querySelectorAll('.btn-delete');
    const seeMoreBtns = document.querySelectorAll('.btn-see-more');
  
	// Handle title clicks for long titles
    const artworkTitles = document.querySelectorAll('.artwork-title');
    
    artworkTitles.forEach(title => {
        // Check if title is truncated
        if (title.offsetWidth < title.scrollWidth) {
            title.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                
                // Fetch title and description
                fetch(`/get_description/${id}`)
                    .then(response => response.json())
                    .then(data => {
                        // Set modal content
                        document.getElementById('view-title').textContent = data.title;
                        document.getElementById('view-description-text').textContent = data.description;
                        
                        // Show modal
                        viewDescriptionModal.style.display = 'block';
                    });
            });
        }
    });
	
    // Close buttons
    const closeButtons = document.querySelectorAll('.close');
    
    // Add Artwork button
    addArtworkBtn.addEventListener('click', function() {
        addArtworkModal.style.display = 'block';
    });
    
    // Edit buttons
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const title = this.getAttribute('data-title');
            const description = this.getAttribute('data-description');
            
            // Set form action
            document.getElementById('edit-form').action = `/edit/${id}`;
            
            // Fill form fields
            document.getElementById('edit-title').value = title || '';
            document.getElementById('edit-description').value = description;
            
            // Show modal
            editArtworkModal.style.display = 'block';
        });
    });
    
    // Delete buttons
    let artworkToDelete = null;
    
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            artworkToDelete = this.getAttribute('data-id');
            deleteConfirmModal.style.display = 'block';
        });
    });
    
    // Confirm delete button
    document.getElementById('confirm-delete').addEventListener('click', function() {
        if (artworkToDelete) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/delete/${artworkToDelete}`;
            document.body.appendChild(form);
            form.submit();
        }
    });
    
    // Cancel delete button
    document.getElementById('cancel-delete').addEventListener('click', function() {
        deleteConfirmModal.style.display = 'none';
        artworkToDelete = null;
    });
    
    // See more buttons
    seeMoreBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            
            // Fetch full description
            fetch(`/get_description/${id}`)
                .then(response => response.json())
                .then(data => {
                    // Set modal content
                    document.getElementById('view-title').textContent = data.title || '';
                    document.getElementById('view-description-text').textContent = data.description;
                    
                    // Show modal
                    viewDescriptionModal.style.display = 'block';
                });
        });
    });
    
    // Close buttons
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            modal.style.display = 'none';
            if (modal === deleteConfirmModal) {
                artworkToDelete = null;
            }
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
            if (event.target === deleteConfirmModal) {
                artworkToDelete = null;
            }
        }
    });
});
