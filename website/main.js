// Fetch and display bios for Hugh Brien and Darrell Dunn

document.addEventListener('DOMContentLoaded', () => {
    const hughBio = `Hugh Brien is a seasoned cloud architect with over 20 years of experience in designing and deploying enterprise-grade cloud solutions. He specializes in automation, security, and scalable infrastructure.`;
    const darrellBio = `Darrell Dunn is a solutions engineer with a passion for building resilient and efficient cloud systems. He brings deep expertise in DevOps, CI/CD, and cloud-native technologies.`;

    document.querySelector('#hugh-profile .bio').textContent = hughBio;
    document.querySelector('#darrell-profile .bio').textContent = darrellBio;
}); 