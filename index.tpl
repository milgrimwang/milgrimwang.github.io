<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{{ title }}</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="shortcut icon" href="/favicon.ico">
    <style>
        body {
            background-color: #333;
            color: #fff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        h1 {
            text-align: center;
            margin: 20px 0;
            color: #fff;
        }

        .links-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        a {
            display: block;
            color: #fff;
            text-decoration: none;
            background-color: #555;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            word-wrap: break-word;
        }

        a:hover {
            background-color: #777;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    Last updated: {updated_at}
    <div class="links-container">
        <ul>
            {% for link in links %}
                <li>
                    <a href="{{ link.url }}">{{ link.time }} | {{ link.text }}</a>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
