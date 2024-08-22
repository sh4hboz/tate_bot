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

document.querySelectorAll('.yes').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();

        const itemId = this.getAttribute('data-item-id');
        const buyModal = this.closest('.buy_modal');
        const typesItem = this.closest('.types_item');

        fetch('/buy_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Token': 'q6AUI7RYhksYMQ2HbhDDBA6pA16HS4l4YGYbgvn/OfKXyuEjfPPTMlb?BNC-?NWbC168ne0r8=zDWmAPHe3ogFQdNimC4UfVhK?L41wqn1D?2qOZn2YntAf=JTUG5gg=949v697L-DD5aU9Zm1peZDQ!QPLq1lNOLUPC?BPGe4hsK=ClQw!6Gvv7uhPZNWUUaIJDYS?oA/Eq6k!EcK8u-TE3X8jAyPxc4gnywT24LSAu2GStTkc/1BvkukuKC85x'
            },
            body: JSON.stringify({
                item_id: itemId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                buyModal.classList.remove('modal_open')
                typesItem.classList.remove('item')
                update_data();
            } else {
                console.error(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

function update_data() {
    const userId = 1; // Foydalanuvchi ID

    const url = new URL('/get_user', window.location.origin);
    url.searchParams.append('user_id', userId);

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Token': 'q6AUI7RYhksYMQ2HbhDDBA6pA16HS4l4YGYbgvn/OfKXyuEjfPPTMlb?BNC-?NWbC168ne0r8=zDWmAPHe3ogFQdNimC4UfVhK?L41wqn1D?2qOZn2YntAf=JTUG5gg=949v697L-DD5aU9Zm1peZDQ!QPLq1lNOLUPC?BPGe4hsK=ClQw!6Gvv7uhPZNWUUaIJDYS?oA/Eq6k!EcK8u-TE3X8jAyPxc4gnywT24LSAu2GStTkc/1BvkukuKC85x'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            const balanceElement = document.querySelector('.balance_text span');
            balanceElement.innerText = `${data.balance} `;
            // Boshqa kerakli ma'lumotlarni ham yangilashingiz mumkin
        } else {
            console.error('Error updating data:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateItems() {
    const userId = 1;
    const url = new URL('/get_user_items', window.location.origin);
    url.searchParams.append('user_id', userId);

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Token': 'q6AUI7RYhksYMQ2HbhDDBA6pA16HS4l4YGYbgvn/OfKXyuEjfPPTMlb?BNC-?NWbC168ne0r8=zDWmAPHe3ogFQdNimC4UfVhK?L41wqn1D?2qOZn2YntAf=JTUG5gg=949v697L-DD5aU9Zm1peZDQ!QPLq1lNOLUPC?BPGe4hsK=ClQw!6Gvv7uhPZNWUUaIJDYS?oA/Eq6k!EcK8u-TE3X8jAyPxc4gnywT24LSAu2GStTkc/1BvkukuKC85x'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            const items = data.items;

            const itemCounts = {};
            const lastItemTimes = {};

            items.forEach(item => {
                if (itemCounts[item.id]) {
                    itemCounts[item.id]++;
                } else {
                    itemCounts[item.id] = 1;
                }
                lastItemTimes[item.id] = item.complete_time;
            });

            const itemsContainer = document.querySelector('footer .modal_content');
            itemsContainer.innerHTML = ''; // Avvalgi itemlarni o'chirish

            for (const [itemId, count] of Object.entries(itemCounts)) {
                const item = items.find(item => item.id === parseInt(itemId));
                const completeTime = lastItemTimes[itemId];
                const completeTimeHours = Math.floor(completeTime / 3600);
                const completeTimeMinutes = Math.floor((completeTime % 3600) / 60);

                const itemHTML = `
                    <div class="modal_item">
                        <div class="item_image">
                            ${count > 1 ? `${count}X` : ''}
                            <img src="${item.icon_path}" alt="${item.name}">
                        </div>
                        <div class="item_text">
                            <span class="hour">${completeTimeHours} hours</span>
                            <span class="minut">${completeTimeMinutes} minutes</span>
                        </div>
                    </div>
                `;

                itemsContainer.insertAdjacentHTML('beforeend', itemHTML);
            }
        } else {
            console.error('Error updating items:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
