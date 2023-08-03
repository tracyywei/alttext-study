$(document).ready(function () {
  var suggestions = suggestionsData;
  var clickedWords = new Set(); // Store the already clicked misspelled words

  $("#textarea").on("click", ".misspelled", function () {
    var word = $(this).data("word");
    if (!clickedWords.has(word)) {
      clickedWords.add(word);
      var suggestion = suggestions[word];
      console.log(suggestion);
      var elem = document.querySelector("#suggestionCard").cloneNode(true);
      elem.classList.remove("hidden");
      elem.querySelector("#error").textContent = "Spelling mistake for " + word;
      elem.querySelector("#suggestions").textContent = "You may mean: " + suggestion;
      elem.querySelector(".suggButton").addEventListener("click", function () {
        elem.remove();
        $(".misspelled[data-word='" + word + "']").removeClass("misspelled");
      });
      document.querySelector("#suggContainer").append(elem);
    }
  });
});