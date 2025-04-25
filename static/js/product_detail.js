document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Get the size selector element
    const sizeSelector = document.getElementById('id_product_size');
    console.log('Size selector element:', sizeSelector);
    
    // If the size selector exists (product has sizes)
    if (sizeSelector) {
        console.log('Size selector found, making visible');
        // Make sure it's visible
        sizeSelector.style.display = 'block';
        sizeSelector.parentElement.style.display = 'block';
        
        // Add some visual feedback
        sizeSelector.classList.add('border', 'border-dark');
    } else {
        console.log('No size selector found');
    }
}); 