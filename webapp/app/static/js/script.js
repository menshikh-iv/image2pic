$("#dataform").submit(function(e) {
    e.preventDefault();
    alert("WER");

    console.log($("#dataform").serialize());
    //var formData = new FormData($("#dataform"));
    var fromData = false;
    //console.log(formData);
    $.ajax({
           type: "POST",
           url: "/processing",
           data: $("#dataform").serialize(),
           success: function(data)
           {
               alert(data);
           }
         });

    e.preventDefault();

});

function send_vote(self, vote){
    var uvote = parseInt(vote);
    var row = $(self).closest("tr");
    var dist = parseFloat(row.find("td#dist").text());
    var text = row.find("td#text").text();
    var img_url = row.find("td>img#img_url").attr("src");

    var query_text = $("table>tbody>tr>td#query_text").text();
    var query_img = $("table>tbody>tr>td>img#query_img").attr("src");
    var query_img_src = query_img ? query_img : "";

    console.log(JSON.stringify({
        "dist": dist,
        "text": text,
        "img_url": img_url,
        "query_text": query_text,
        "query_img": query_img_src,
        "vote": uvote
    }));

    var td = $(self).closest("td");
    td.find("button").remove();
    (uvote == 1) ? td.attr("bgcolor", "#5cb85c") : td.attr("bgcolor", "#c9302c");
}