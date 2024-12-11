document.addEventListener("DOMContentLoaded", function () {
    const swipeArea = document.getElementById('swipeArea');
    const noRecommendationsCard = document.getElementById('no-recommendations-card');
    const buttonsBar = document.querySelector('#buttons-bar');
    const likeButton = document.querySelector('.button.like');
    const dislikeButton = document.querySelector('.button.dislike');
    let currentCardIndex = 0;

    // create a card to show with all the pal date
    function createCard(user) {
        const card = document.createElement('div');
        card.className = 'card';
        card.id = `card-${user.id}`;
        card.innerText = `Pal name: ${user.first_name} ${user.last_name}\n
                      Travel to: ${user.destination}\n
                      From the: ${user.start_date}\n
                      Until the: ${user.end_date}`;
        swipeArea.appendChild(card);
        
        // can be use with a mouse or with touch (for phones and touch screen)
        card.addEventListener('mousedown', startDrag); 
        card.addEventListener('touchstart', startDrag);
    }

    function showNoRecommendations() {
        noRecommendationsCard.style.display = 'flex';
        buttonsBar.style.display = 'none';
    }

    function loadNextCard() {
        if (currentCardIndex < trips_scores.length) {
            createCard(trips_scores[currentCardIndex]);
        } else {
            showNoRecommendations();
        }
    }
  
    // when there are no more users to show write a messege.
    if (trips_scores.length === 0) {
        showNoRecommendations();
    } else {
        loadNextCard();
    }

    function startDrag(e) {
        e.preventDefault(); // prevent default drag behavior
        const card = e.target; //get the card being dragged
        let startX, startY;
        startX = e.touches ? e.touches[0].clientX : e.clientX; // get initial X position
        startY = e.touches ? e.touches[0].clientY : e.clientY; // get initial Y position

        // event listeners for dragging and end drag
        document.addEventListener('mousemove', drag);
        document.addEventListener('touchmove', drag);
        document.addEventListener('mouseup', endDrag);
        document.addEventListener('touchend', endDrag);

        function drag(e) {
            const clientX = e.touches ? e.touches[0].clientX : e.clientX; // get current X position
            const diffX = clientX - startX;
            const rotationAngle = diffX / 10; //calculate rotation angle based on X difference

            card.style.transform = `translate(${diffX}px, 0) rotate(${rotationAngle}deg)`; // apply transform to the card

            if (diffX > 0) {
                card.classList.add('like');
                card.classList.remove('dislike');
            } else if (diffX < 0) {
                card.classList.add('dislike');
                card.classList.remove('like');
            } else {
                card.classList.remove('like', 'dislike'); // remove both classes if no movement
            }
        }

        function endDrag(e) {
            const clientX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX; // get final X position
            const diffX = clientX - startX; //calculate difference in X position
            if (Math.abs(diffX) > 100) {
                if (diffX > 0) {
                    // move card right - mark like.
                    card.style.transform = `translate(${1000}px, 0) rotate(30deg)`; 
                    card.style.opacity = 0;
                    console.log(`Liked ${card.innerText}!`);

                    // fetch the "like" to the server. useing the api "like" in the app.py
                    fetch(`/like?me=${my_id}&pal=${trips_scores[currentCardIndex]['id']}`, {
                        method: 'GET'
                    }).catch(error => console.error('Error:', error));


                } else {
                    card.style.transform = `translate(${-1000}px, 0) rotate(-30deg)`; // move card left
                    card.style.opacity = 0;
                }

                setTimeout(() => {
                    swipeArea.removeChild(card);
                    currentCardIndex++;
                    loadNextCard();
                }, 300);
            } else {
                card.style.transform = 'translate(0, 0) rotate(0deg)';
                card.classList.remove('like', 'dislike');
            }
            // remove event listeners for dragging and end drag
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('touchmove', drag);
            document.removeEventListener('mouseup', endDrag);
            document.removeEventListener('touchend', endDrag);
        }
    }

    likeButton.addEventListener('click', () => swipeCard('right'));
    dislikeButton.addEventListener('click', () => swipeCard('left'));


    function swipeCard(direction) {
    // Select the first card that is not the "no recommendations" card
        const card = document.querySelector('.card:not(#no-recommendations-card)');
        if (!card) return;
        if (direction === 'right') {
            card.classList.add('like'); // Add the "like" class to the card
            card.classList.remove('dislike'); // Remove the "dislike" class from the card
            setTimeout(() => {
                card.style.transform = `translate(${1000}px, 0) rotate(30deg)`; // move card right
                card.style.opacity = 0;
                setTimeout(() => {
                    swipeArea.removeChild(card); // Remove the card from the swipe area
                    currentCardIndex++;
                    loadNextCard(); // Load the next card
                }, 300);
            }, 100);
        } else if (direction === 'left') {
            card.classList.add('dislike'); // Add the "dislike" class to the card
            card.classList.remove('like'); // Remove the "like" class from the card
            setTimeout(() => {
                card.style.transform = `translate(${-1000}px, 0) rotate(-30deg)`; // move card right
                card.style.opacity = 0;
                setTimeout(() => {
                    swipeArea.removeChild(card); // Remove the card from the swipe area
                    currentCardIndex++;
                    loadNextCard(); // Load the next card
                }, 300);
            }, 100);
        }
    }
});