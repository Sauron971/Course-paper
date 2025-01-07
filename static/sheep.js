document.addEventListener('DOMContentLoaded', function() {
    const hdmiButton = document.getElementById('hdmi');
    let sheep;
    let animationFrame;
    let targetX, targetY;
    let speed = 0.5;
    let intervalTime = 3000;
    let moving = false;
    let timerId;
    let lastX = 0;
    const staticImage = '../static/images/sheep_static.png';

    function initSounds() {
            appearSound = new Audio('../static/sheep_appear.m4a');
            disappearSound = new Audio('../static/sheep_disappear.m4a');
    }

    initSounds();
    hdmiButton.addEventListener('click', function() {
        if (!sheep) {
            sheep = document.createElement('img');
            sheep.src = '../static/images/sheep.gif';
            sheep.classList.add('sheep');
            document.body.appendChild(sheep);
            lastX = parseFloat(sheep.style.left || 0);
             setNewTarget();
            moveSheep();
            appearSound.play();
        } else {
            stopSheep();
            sheep.remove();
            sheep = null;
            disappearSound.play();
        }
    });

    function setNewTarget() {
        targetX = Math.random() * (window.innerWidth - sheep.offsetWidth);
        targetY = Math.random() * (window.innerHeight - sheep.offsetHeight);
    }

    function moveSheep() {
        if (moving) return;
        moving = true;
        sheep.src = '../static/images/sheep.gif';
        function animate() {
            const currentX = parseFloat(sheep.style.left || 0);
            const currentY = parseFloat(sheep.style.top || 0);

            const dx = targetX - currentX;
            const dy = targetY - currentY;

            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 1) {
                const stepX = dx / distance * speed;
                const stepY = dy / distance * speed;
                if (stepX > 0 && sheep.style.transform === 'scaleX(-1)') {
                    sheep.style.transform = 'scaleX(1)';
                } else if (stepX < 0 && sheep.style.transform !== 'scaleX(-1)') {
                    sheep.style.transform = 'scaleX(-1)';
                }
                sheep.style.left = (currentX + stepX) + 'px';
                sheep.style.top = (currentY + stepY) + 'px';
                lastX = currentX;
                 animationFrame = requestAnimationFrame(animate);
            } else {
               moving = false;
			   sheep.src = staticImage;
               timerId = setTimeout(() => {
                    setNewTarget();
                    moveSheep();
                }, intervalTime);
            }
        }
       animationFrame = requestAnimationFrame(animate);
    }

     function stopSheep() {
        cancelAnimationFrame(animationFrame);
        clearTimeout(timerId);
        moving = false;
    }
});