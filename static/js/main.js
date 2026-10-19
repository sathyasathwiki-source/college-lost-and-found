/**
 * main.js — Campus Lost & Found
 * Vanilla JS for useful UI interactions only.
 * No frameworks. No dependencies.
 */

/* =========================================================================
   1. Mobile Navigation Toggle
   ========================================================================= */
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Close when clicking outside
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();


/* =========================================================================
   2. Flash message auto-dismiss (after 6 seconds)
   ========================================================================= */
(function () {
  const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 400);
    }, 6000);
  });
})();


/* =========================================================================
   3. Confirm before form submission for destructive actions
   ========================================================================= */
(function () {
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const msg = el.getAttribute('data-confirm');
      if (!confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });
})();


/* =========================================================================
   4. Set today's date as the default and maximum for date inputs
   ========================================================================= */
(function () {
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"].max-today').forEach(function (el) {
    el.setAttribute('max', today);
    if (!el.value) {
      el.value = today;
    }
  });
})();


/* =========================================================================
   5. Image preview before upload
   ========================================================================= */
(function () {
  const fileInput = document.getElementById('image');
  const preview   = document.getElementById('image-preview');
  if (!fileInput || !preview) return;

  fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (!file) {
      preview.src = '';
      preview.style.display = 'none';
      return;
    }

    // Validate type client-side (server validates again)
    const allowed = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowed.includes(file.type)) {
      showError('Invalid file type. Allowed: PNG, JPG, GIF, WEBP.');
      fileInput.value = '';
      return;
    }

    // Validate size client-side (max 5 MB)
    if (file.size > 5 * 1024 * 1024) {
      showError('File is too large. Maximum size is 5 MB.');
      fileInput.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  });

  function showError(msg) {
    let el = document.getElementById('upload-error');
    if (!el) {
      el = document.createElement('p');
      el.id = 'upload-error';
      el.className = 'alert alert-error mt-1';
      fileInput.parentNode.appendChild(el);
    }
    el.textContent = msg;
    setTimeout(function () { if (el.parentNode) el.remove(); }, 5000);
  }
})();


/* =========================================================================
   6. Filter form — Clear Filters button
   ========================================================================= */
(function () {
  const clearBtn = document.getElementById('clear-filters');
  if (!clearBtn) return;

  clearBtn.addEventListener('click', function () {
    const form = clearBtn.closest('form');
    if (!form) return;
    form.querySelectorAll('input, select').forEach(function (el) {
      el.value = '';
    });
    form.submit();
  });
})();


/* =========================================================================
   7. Active navigation link highlighting
   ========================================================================= */
(function () {
  const path  = window.location.pathname;
  const links = document.querySelectorAll('.nav-links a');
  links.forEach(function (link) {
    const href = link.getAttribute('href');
    if (!href) return;
    // Exact match or starts-with (for sub-pages)
    if (path === href || (href !== '/' && path.startsWith(href))) {
      link.classList.add('active');
    }
  });
})();


/* =========================================================================
   8. Form validation — required field highlighting
   ========================================================================= */
(function () {
  document.querySelectorAll('form.validated-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      let valid = true;
      form.querySelectorAll('[required]').forEach(function (field) {
        const wrapper = field.closest('.form-group');
        if (!field.value.trim()) {
          valid = false;
          field.style.borderColor = '#c0392b';
          if (wrapper) {
            let msg = wrapper.querySelector('.field-error');
            if (!msg) {
              msg = document.createElement('span');
              msg.className = 'field-error form-help';
              msg.style.color = '#c0392b';
              wrapper.appendChild(msg);
            }
            msg.textContent = 'This field is required.';
          }
        } else {
          field.style.borderColor = '';
          if (wrapper) {
            const msg = wrapper.querySelector('.field-error');
            if (msg) msg.remove();
          }
        }
      });
      if (!valid) e.preventDefault();
    });
  });
})();


/* =========================================================================
   9. Smooth scroll for anchor links
   ========================================================================= */
document.querySelectorAll('a[href^="#"]').forEach(function (a) {
  a.addEventListener('click', function (e) {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
