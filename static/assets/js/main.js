// Solo Leveling System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Level up animation
    function playLevelUpAnimation() {
        const levelBadge = document.querySelector('.level-badge');
        if (levelBadge) {
            levelBadge.classList.add('pulse');
            setTimeout(() => {
                levelBadge.classList.remove('pulse');
            }, 2000);
        }
    }

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });

    // Quest completion handler
    function completeQuest(questId) {
        // Add glowing effect
        const questCard = document.querySelector(`#quest-${questId}`);
        if (questCard) {
            questCard.classList.add('glow-effect');
            
            // Play completion sound
            const completionSound = new Audio('/static/assets/sounds/complete.mp3');
            completionSound.play();
            
            // Update XP and progress
            updateProgress();
        }
    }

    // XP gain animation
    function showXPGain(amount) {
        const xpPopup = document.createElement('div');
        xpPopup.classList.add('xp-popup');
        xpPopup.textContent = `+${amount} XP`;
        document.body.appendChild(xpPopup);
        
        setTimeout(() => {
            xpPopup.classList.add('fade-out');
            setTimeout(() => {
                xpPopup.remove();
            }, 1000);
        }, 2000);
    }

    // Buff timer updates
    function updateBuffTimers() {
        const buffTimers = document.querySelectorAll('.buff-timer');
        buffTimers.forEach(timer => {
            const timeLeft = parseInt(timer.getAttribute('data-time-left'));
            if (timeLeft > 0) {
                timer.setAttribute('data-time-left', timeLeft - 1);
                timer.textContent = formatTime(timeLeft - 1);
            } else {
                timer.closest('.buff-item').classList.add('fade-out');
            }
        });
    }

    // Format time helper
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    // Initialize buff timer updates
    setInterval(updateBuffTimers, 1000);

    // Achievement unlock animation
    function unlockAchievement(achievementId) {
        const achievement = document.querySelector(`#achievement-${achievementId}`);
        if (achievement) {
            achievement.classList.add('unlocked', 'float');
            
            // Show congratulations modal
            const modal = new bootstrap.Modal(document.getElementById('achievementModal'));
            modal.show();
            
            // Play unlock sound
            const unlockSound = new Audio('/static/assets/sounds/unlock.mp3');
            unlockSound.play();
        }
    }

    // Rank up animation
    function rankUp(newRank) {
        const rankBadge = document.querySelector('.rank');
        if (rankBadge) {
            rankBadge.classList.add('pulse');
            setTimeout(() => {
                rankBadge.className = `rank rank-${newRank.toLowerCase()}`;
                rankBadge.textContent = `${newRank}-Rank`;
            }, 1000);
        }
    }

    // Initialize dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.btn-icon');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (trigger && menu) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('show');
            });
        }
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    });

    // Quest filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const questCards = document.querySelectorAll('.quest-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');
            
            questCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update active filter
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
});

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show scroll to top button when scrolling down
window.addEventListener('scroll', () => {
    const scrollBtn = document.querySelector('.scroll-top');
    if (scrollBtn) {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    }
});
