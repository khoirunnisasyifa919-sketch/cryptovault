// Menutup notifikasi
function dismissAlert(alertId) {
    const alertEl = document.getElementById(alertId);

    if (alertEl) {
        alertEl.style.opacity = '0';
        setTimeout(() => {
            alertEl.remove();
        }, 300);
    }
}

// Konfirmasi hapus lagu
function confirmDelete(button, songTitle) {
    const message = `Apakah Anda yakin ingin menghapus lagu "${songTitle}"?`;

    if (confirm(message)) {
        button.closest('form').submit();
    }
}

// Auto close alert setelah 5 detik
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach((alert) => {
        alert.style.transition = 'opacity 0.3s ease';

        setTimeout(() => {
            alert.style.opacity = '0';

            setTimeout(() => {
                alert.remove();
            }, 300);

        }, 5000);
    });
});

// Salin Hash SHA-256 Lagu
function copyHash() {
    const hashElement = document.getElementById('digestHash');

    if (hashElement) {
        const hashText = hashElement.innerText;

        navigator.clipboard.writeText(hashText)
            .then(() => {
                alert('Hash SHA-256 lagu berhasil disalin!');
        });
    }
}
