

const ages = [4, 5, 7]
let i = 0



function pupil(arr) {
    for (let i = 0; i < arr.length; i++) {
        const age = arr[i]
        return `pupil ages ${age}`
    }
 
}

//import { age } from '../js/age.json'
const student_age = require('../jstudent_age.json')

//const getCummulative = document.getElementById('get-cummulative')

function get_cummulative(arr){

    return arr.reduce((cumm, totalPrice) => {
        return cumm + totalPrice.age
    }, 0)
}

console.log(get_cummulative(student_age))