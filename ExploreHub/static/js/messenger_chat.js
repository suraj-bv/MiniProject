// when the user press the button it will show the Messenger chat
document.addEventListener("DOMContentLoaded", () => {
        const buttons = document.querySelectorAll(".chatButton");

        // Attach event listeners to each chat button
        buttons.forEach(button => {
            button.addEventListener("click", (event) => {
            // Load all the necessary data from the button's data attributes
                const palId = button.getAttribute('data-pal-id');
                const palName = button.getAttribute('data-pal-name');
                const palEmail = button.getAttribute('data-pal-email');
                const myId = button.getAttribute('data-me-id');
                const myName = button.getAttribute('data-me-name');
                const containerId = `talkjs-container-${palId}`;

                // Load the TalkJS script and initialize the TalkJS API
                (function(t, a, l, k, j, s) {
                    s = a.createElement('script');
                    s.async = 1;
                    s.src = 'https://cdn.talkjs.com/talk.js';
                    a.head.appendChild(s);
                    k = t.Promise;
                    t.Talk = {
                        v: 3,
                        ready: {
                            then: function(f) {
                                if (k) return new k(function(r, e) { l.push([f, r, e]) });
                                l.push([f])
                            },
                            catch: function() { return k && new k() },
                            c: l
                        }
                    };
                })(window, document, []);

                 // Once TalkJS is ready, set up the chat session and conversation
                Talk.ready.then(function () {
                    const me = new Talk.User({
                        id: myId,
                        name: myName,
                    });

                    const session = new Talk.Session({
                        appId: 'tPHzLSkE',
                        me: me,
                    });

                    const other = new Talk.User({
                        id: palId,
                        name: palName,
                        email: palEmail,
                    });

                    // Create a one-on-one conversation between the two users
                    const conversation = session.getOrCreateConversation(Talk.oneOnOneId(me, other));
                    conversation.setParticipant(me);
                    conversation.setParticipant(other);

                    // Create and mount the chatbox for the conversation
                    const chatbox = session.createChatbox();
                    chatbox.select(conversation);
                    chatbox.mount(document.getElementById(containerId));
                    document.getElementById(containerId).style.display = 'block';
                }).catch(error => {
                    console.error("TalkJS Initialization Error:", error);
                });
            });
        });
    });