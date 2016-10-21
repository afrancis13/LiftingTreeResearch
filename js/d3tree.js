var width = 900,
    height = 680;

var tree = d3.layout.tree()
    .size([width - 20, height - 20]);

var root = {},
    nodes = tree(root);

root.parent = root;
root.px = root.x;
root.py = root.y;

var diagonal = d3.svg.diagonal();

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(10,10)");

$("svg").css({top: 30, position: "absolute"})

var node = svg.selectAll(".node"),
    link = svg.selectAll(".link");

var type = getParameterByName("type");
var nodeLimit = getParameterByName("limit");

if (type == null) {
  type = "rrt";
}

var branchingFactor;
if (type == "dary") {
  branchingFactor = getParameterByName("d");  
} else {
  branchingFactor = null;
}

var duration = 300,
    timer = setInterval(update, duration, nodeLimit, branchingFactor);

// Fixes a bug in which the first update is labeled as "2"
var first = true;

var parameterName

function renderTree() {
  // Recompute the layout and data join.
  node = node.data(tree.nodes(root), function(d) { return d.id; });
  link = link.data(tree.links(nodes), function(d) { return d.source.id + "-" + d.target.id; });

  // Add entering nodes in the parent’s old position.
  node.enter().append("circle")
      .attr("class", "node")
      .attr("r", 4)
      .attr("cx", function(d) { return d.parent.px; })
      .attr("cy", function(d) { return d.parent.py; })
  
  node.enter().append("text")
    .attr("class", "node")
    .attr("x", function(d) { return d.parent.px; })
    .attr("y", function(d) { return d.parent.py + 10; })
    .text(function() {
      if (first) {
        first = false;
        return "1"
      } else {
        return nodes.length.toString()        
      }
    })

  var nodeExit = node.exit().transition()
    .duration(duration)
    .attr("transform", function(d) {
      return "translate(" + d.source.y + "," + d.source.x + ")";
    })
    .remove()

  nodeExit.select("circle")
    .attr("r", 1e-6)

  nodeExit.select("text")
    .style("fill-opacity", 1e-6)

  // Add entering links in the parent’s old position.
  link.enter().insert("path", ".node")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: d.source.px, y: d.source.py};
        return diagonal({source: o, target: o});
      });

  link.exit()
    .attr("d", function(d) {
      var o = {
        x: d.source.x,
        y: d.source.y
      };
      return diagonal({
        source: o,
        target: o
      });
    })
    .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });

  // Transition nodes and links to their new positions.
  var t = svg.transition()
      .duration(duration);

  t.selectAll(".link")
      .attr("d", diagonal);

  t.selectAll(".node")
      .attr("x", function(d) { return d.px = d.x + 10; })
      .attr("y", function(d) { return d.py = d.y + 5 })
      .attr("cx", function(d) { return d.px = d.x; })
      .attr("cy", function(d) { return d.py = d.y; });
}

function update(nodeLimit, branchingFactor) {
  // Instantiate default values, especially for the initial load
  // of the page.
  if (nodeLimit == null) {
    nodeLimit = 20
  }

  if (branchingFactor == null) {
    branchingFactor = Number.POSITIVE_INFINITY
  }

  if (nodes.length >= nodeLimit) return clearInterval(timer);

  // Add a new node to a random parent.
  var n = {id: nodes.length},
      p = chooseRandom();

  if (typeof p.children != "undefined" && p.children.length > 0) {
    p.children.push(n);
  } else {
    p.children = [n];
  }

  nodes.push(n);

  renderTree()
}


/* Exponential random number generator
 * Time until next arrival. */

/* http://en.wikipedia.org/wiki/Exponential_distribution#Generating_exponential_variates. */
function randomExponential(rate) {
  rate = rate || 1;
  U = Math.random();

  return -Math.log(U) / rate;
}

function lift() {
  var exponentialDraws = [];

  var currentNode;

  for (var i = 0; i < nodes.length; i++) {
    currentNode = nodes[i | 0];
    if (typeof currentNode.children != "undefined" && currentNode.children.length > 0) {
      exponentialDraws.append(randomExponential(currentNode.children.length));
    } else {
      exponentialDraws.append(Number.POSITIVE_INFINITY);
    }
  }

  var invalidatedNodes = [];
  var currentNode;
  var minWaitTime;
  var liftedNode;
  while (invalidatedNodes.length < nodes.length) {
    minWaitTime = Number.POSITIVE_INFINITY;
    liftedNode = null;
    for (var j = 0; j < nodes.length; j++) {
      currentNode = nodes[j];
      if (invalidatedNodes.indexOf(currentNode) == -1) {
        if (exponentialDraws[j] < minWaitTime) {
          minWaitTime = exponentialDraws[j];
          liftedNode = currentNode;
        }
      }
    }

    /* Now, invalidate the entire subtree. */
    invalidatedSubtree = getSubtree(liftedNode, []);

    /* Javascript version of .extend(). */
    invalidatedNodes.push.apply(invalidatedNodes, invalidatedSubtree);

    /* At last, place a mark on the correct edge. */
    // TODO.
  }
}

function getSubtree(n, ns) {
  if (n.children) {
    n.children.forEach(function(c) {
      if (c.id != target.id) {
        ns = getSubtree(c, ns);        
      }
    });
    ns.push(n);
  }
  return ns;
}

// function removeNode(d) {
//   var subtree = [];
//   var children = getSubtree(d, d.parent, subtree);
//   d.parent.children = children;
//   d.parent.children.forEach(function(child) {
//     nodeIndex = nodes.indexOf(child);
//     nodes.splice(nodeIndex, 1)
//     var validNodesIndex = validNodes.indexOf(child);
//     if (validNodesIndex != -1) {
//       validNodes.splice(validNodesIndex, 1);
//     }
//   });
//   renderTree()
// }

/* Chooses a random node based on the construction constraints.
 * This is a more general version of the algorithm proposed in
 * bit.py. */
function chooseRandom() {
  if (type == "dary") {
    if (nodes.length > 1) {
      var min = 0;
      var max = nodes.length * (parseInt(branchingFactor) - 1);
      var rand = Math.floor(Math.random() * (max - min + 1)) + min;

      var degree = 0;
      var currentNode;

      for (var i = 0; i < nodes.length; i++) {
        currentNode = nodes[i | 0];

        if (typeof currentNode.children != "undefined" && currentNode.children.length < parseInt(branchingFactor)) {
          degree += (parseInt(branchingFactor) - currentNode.children.length);
        }

        if (degree > rand) {
          break;
        }
      }
      return currentNode;    
    } else {
      return nodes[0 | 0];
    }      
  } else if (type == "rrt") {
    var min = 0;
    var max = nodes.length - 1;
    var rand = Math.floor(Math.random() * (max - min + 1)) + min;
    return nodes[rand | 0]; 
  }
}

function lift() {
  if (nodes.length > 1) {
  }
}

/* Get parameter by name for query string. Found on SO.
 * http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript.
 * Lots of people complained about it, but works for me (shrug emoji). */
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

/* Respond to other button! */
$("#otherButton").change(function() {
  $("#branchFactorInput").css("visibility", "visible");
});


/* Respond to other button! */
$("#daryButton").change(function() {
  $("#daryMenu").css("visibility", "visible");
});

/* Respond to submit button! */
$("#options-submit").click(function() {
  var numNodes = $("#num-nodes").val();

  var rrt = $("#rrtButton").is(":checked");
  var dary = $("#daryButton").is(":checked");

  var query;

  if (dary) {
    var binary = $("#binaryButton").is(':checked');
    var ternary = $("#ternaryButton").is(':checked');
    var any = $("#anyButton").is(':checked');
    var other = $("#otherButton").is(':checked');
    var d = $("#branchFactorInput").val();
    var branchingFactor;

    /* Construct the query string. */
    if (binary) {
      branchingFactor = "2";
      query = "?" + "type=dary" + "&d=" + branchingFactor + "&limit=" + numNodes;
    } else if (ternary) {
      branchingFactor = "3";
      query = "?" + "type=dary" + "&d=" + branchingFactor + "&limit=" + numNodes;
    } else if (any) {
      branchingFactor = "";
      query = "?" + "type=dary" + "&d=" + branchingFactor + "&limit=" + numNodes;
    } else if (other) {
      branchingFactor = d;
      query = "?" + "type=dary" + "d=" + branchingFactor + "&limit=" + numNodes;
    }
  } else {
    query = "?" + "type=rrt" + "&limit=" + numNodes;
  }

  /* Close Modal. */
  $("#createModal").modal("toggle")

  /* Reload page. */
  window.location.href = window.location.href.replace( /[\?#].*|$/, query);
});
