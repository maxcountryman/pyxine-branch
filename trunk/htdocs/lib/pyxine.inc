<?php // -*-php-*-

class Index {
  function Index($ind) {
    $this->index = $ind;
    $this->selected = "";
  }

  function set_selected($name) {
    $this->selected = $name;
  }
  
  function as_html () {
    foreach ($this->index as $head => $list) {
      $html[] = sprintf('<strong class="h2">%s%s<span class="hide">:</span></strong>',
                        $sep, htmlspecialchars($head));
      foreach ($list as $text => $url) {
        $id = ($text == $this->selected) ? ' id="selected"' : '';
        $html[] = sprintf('<a href="%s"%s>%s</a>',
                          htmlspecialchars($url),
                          $id,
                          htmlspecialchars($text));
      }
      $sep = '<span class="hide">&nbsp;</span>';
    }
    return join("\n", $html);
  }
}

    
  

$_pages = array("Home" => "http://pyxine.sourceforge.net/");
$_links = array("SF Project Info" =>
                "http://sourceforge.net/projects/pyxine",

                "Downloads" =>
                "http://sourceforge.net/project/showfiles.php?group_id=73236",

                "CVS Repo" =>
                "http://sourceforge.net/cvs/?group_id=73236");

$INDEX = new Index(array("Pages" => $_pages,
                         "Links" => $_links));

class Page {
  function Page($page_title) {
    $this->title = $page_title;
    ob_start();
  }

  function flush() {
    $tmpl['BODY'] = ob_get_contents();
    ob_end_clean();

    $tmpl['TITLE'] = htmlspecialchars($this->title);

    global $INDEX;
    $INDEX->set_selected($this->title);
    $tmpl['INDEX'] = $INDEX->as_html();

    $this->expand_template('lib/pyxine.tmpl', $tmpl);
  }

  function expand_template($tmpl_file, $tmpl_vars) {
    extract($tmpl_vars);
    include($tmpl_file);
  }
}

?>
