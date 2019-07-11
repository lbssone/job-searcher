let catAndActs = {};
catAndActs['時薪'] = [{'name':'150以上', 'value': '150'}, {'name': '200以上', 'value': '200'}, {'name': '250以上','value': '250'}, {'name': '300以上','value': '300'}];
catAndActs['月薪'] = [{'name': '3萬以上', 'value': '30000'}, {'name': '4萬以上', 'value': '40000'}, {'name': '5萬以上', 'value': '50000'}, {'name': '6萬以上', 'value': '60000'}];

function ChangecatList() {
    let catList = document.getElementById("salary-type");
    let actList = document.getElementById("salary");
    let selCat = catList.options[catList.selectedIndex].value;
    while (actList.options.length) {
        actList.remove(0);
    }
    let cats = catAndActs[selCat];
    if (cats) {
        let i;
        for (i = 0; i < cats.length; i++) {
            let cat = new Option(cats[i]['name'], cats[i]['value']);
            actList.options.add(cat);
        }
    }
} 