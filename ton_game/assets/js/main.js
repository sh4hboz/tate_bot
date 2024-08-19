document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const modal = document.querySelector(".modal");
  const miItemsButton = document.querySelector(".mi_items");
  
  // Modalni ochish va yopish uchun miItemsButton bosilishi
  miItemsButton.addEventListener("click", function (e) {
    e.preventDefault();
    if (modal.classList.contains("show")) {
      modal.classList.remove("show");
      body.classList.remove("modal-open");
    } else {
      body.classList.add("modal-open");
      modal.classList.add("show");
    }
  });
  
  // Modalni yopish uchun document ustida click hodisasi
  document.addEventListener("click", function (e) {
    if (modal.classList.contains("show") && !modal.contains(e.target) && e.target !== miItemsButton) {
      modal.classList.remove("show");
      body.classList.remove("modal-open");
    }
  });
  
  


  const header = document.querySelector('.header');
  document.querySelectorAll('.openModal').forEach(trigger => {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      const modalId = this.getAttribute('data-modal');
      const modal = document.querySelector(`.custom_modal[data-modal="${modalId}"]`);
      if (modal) {
        modal.classList.add('active');
      }
      if (header) {
        header.style.opacity = '0';
      }
    });
  });

  document.querySelectorAll('.modal_close').forEach(close => {
    close.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelectorAll('.custom_modal').forEach(modal => {
        modal.classList.remove('active');
      });
      if (header) {
        header.style.opacity = '1';
      }
    });
  });

  const typeItems = document.querySelectorAll(".types_item");
  const modals = document.querySelectorAll(".buy_modal");
  const noButtons = document.querySelectorAll(".no");

  typeItems.forEach(item => {
    const trigger = item.querySelector(".type_price");
    const modal = item.querySelector('.buy_modal');
    
    trigger?.addEventListener("click", () => {
      modals.forEach(modal => modal.classList.remove("modal_open"));
      typeItems.forEach(item => item.classList.remove("item"));
      document.body.classList.remove("modal_opened");

      if (modal) {
        modal.classList.add("modal_open");
      }

      item.classList.add("item");
      console.log(item);
    });
  });

  noButtons.forEach(no => {
    no.addEventListener("click", () => {
      modals.forEach(modal => modal.classList.remove("modal_open"));
      typeItems.forEach(item => item.classList.remove("item"));
      document.body.classList.remove("modal_opened");
    });
  });

  // const modalBody = document.querySelector('.modal_body');
  // const typesItems = document.querySelectorAll('.types_item');
  // const modalHeight = 435; 

  // modalBody.addEventListener('scroll', () => {
  //   typesItems.forEach(item => {
  //     const rect = item.getBoundingClientRect();
  //     const buyModal = item.querySelector('.buy_modal');
  //     if (rect.top < modalBody.offsetTop + modalHeight / 2) {
  //       buyModal.classList.remove('top');
  //     } else {
  //       buyModal.classList.add('top');
  //     }
  //   });
  // });

  const modalBody = document.querySelector('.modal_body');
  const typesItems = document.querySelectorAll('.types_item');
  const modalHeight = 435; // .modal_body ning balandligi

  modalBody.addEventListener('scroll', () => {
      typesItems.forEach(item => {
          const rect = item.getBoundingClientRect();
          const modalRect = modalBody.getBoundingClientRect();
          const buyModal = item.querySelector('.buy_modal');

          if (buyModal) { // buyModal mavjudligini tekshirish
              // types_item ning pastki qismi modal_body ning o'rtasidan pastda bo'lsa, top klassini olib tashlash
              if (rect.bottom < modalRect.top + modalHeight / 2) {
                  buyModal.classList.remove('top');
              } else {
                  buyModal.classList.add('top');
              }
          }
      });
  });


});
