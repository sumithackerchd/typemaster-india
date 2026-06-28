// Hindi Mangal Font Mapping
const mangalMap = {
    'a': 'ा', 'A': 'आ', 's': 'स', 'S': 'श्र', 
    'd': 'द', 'D': 'ध', 'f': 'फ', 'F': 'फ़',
    'g': 'ह', 'G': 'ङ', 'h': 'य', 'H': 'ञ',
    'j': 'त', 'J': 'त्र', 'k': 'क', 'K': 'क्',
    'l': 'ल', 'L': 'ळ', ';': 'च', ':': 'छ',
    // ... yahan aap apni baaki keys add kar sakte hain
};

function getMangalChar(char) {
    return mangalMap[char] || char;
}