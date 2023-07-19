// const correctedText = "{{ corrected_text | safe }}";
// document.querySelector('edited-input').value = correctedText;

// $(document).ready(function () {
//   var suggestions = JSON.parse('{{ suggestions|safe }}');

//   $(".misspelled").click(function () {
//     var word = $(this).data("word");
//     var suggestion = suggestions[word];
//     $("#suggestionCard").text("Spelling mistake for " + word + ". You may mean: " + suggestion);
//   });
// });

var suggestions = JSON.parse('{{ suggestions|safe }}');

for (let s of suggestions) {
  console.log(s);
  var elem = document.querySelector("#suggestionCard").cloneNode(true);
  elem.classList.remove("hidden");
  elem.querySelector("#error").textContent = "Spelling mistake for " + s;
  elem.querySelector("#suggestions").textContent = "You may mean: " + suggestions[s];
  document.querySelector("#suggContainer").append(elem);
}