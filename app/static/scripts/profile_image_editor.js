var palette = [
    "#e80000", //red
    "#e79700", //orange
    "#e6db00", //yellow
    "#92e233", //lightgreen
    "#00c000", //green
    "#01e5f2", //cyan
    "#0082ca", //midblue
    "#0600ee", //blue
    "#ffa6d1", //lightpink
    "#e23eff", //pink
    "#820281", //purple
    "#ffffff", //white
    "#e4e4e4", //lightgrey
    "#888789", //grey
    "#222222", //darkgrey
    "#a16a3f", //brown
]

class ProfileImage {
    constructor(image_canvas, width = 16, height = 16) {
        this.canvas = image_canvas;
        this.width = width;
        this.height = height;

        // Calculate size of an image pixel
        // Canvas must already be square, and preferably have dimensions divisible by 16
        this.pixel_size = this.canvas.getAttribute("width").slice(0, -2) / this.width;

        // Disable right-click menu
        this.canvas.setAttribute('oncontextmenu', 'return false;');
        // Create blank image
        this.clear()
        this.render();
    }

    clear(colour_index = 11) {
        // Fill image with white
        this.image = Array(this.height);
        for (var i = 0; i < this.height; i++) {
            this.image[i] = Array(this.width).fill(colour_index);
        }
    }

    from_base64(base64_string) {
        base64_string = base64_string.replace("\n", "");
        var bin_string = atob(base64_string);
        var flat_image = new Array();

        for (var i = 0; i < bin_string.length; i++) {
            var byte = bin_string[i].charCodeAt();
            flat_image.push(byte >> 4);
            flat_image.push(byte & 15);
        }

        var row = 0;
        for (var i = 0; i < flat_image.length; i += 16) {
            this.image[row] = flat_image.slice(i, i + 16);
            row++
        }
        this.render();
    }

    to_base64() {
        var flat_image = [].concat.apply([], this.image);
        var byte_string = "";
        for (var i = 0; i < flat_image.length; i += 2) {
            var byte = (flat_image[i] << 4) + flat_image[i + 1];
            byte_string += String.fromCharCode(byte);
        }

        var b64_string = btoa(byte_string);
        return b64_string;
    }

    // Draw an outline around the specified pixel
    outline_pixel(coords, colour_index = 12, thickness = 1) {
        var ctx = this.canvas.getContext("2d");

        // Disable anti-aliasing
        // ctx.translate(0.5, 0.5);

        ctx.lineWidth = thickness;
        ctx.strokeStyle = palette[colour_index];
        ctx.strokeRect(
            (coords[0] * this.pixel_size) + (thickness / 2),
            (coords[1] * this.pixel_size) + (thickness / 2),
            this.pixel_size - thickness,
            this.pixel_size - thickness,
        );

        // Re-enable anti-aliasing
        // ctx.translate(-0.5, -0.5);
    }

    // Shows a small square of the chosen colour on the pixel beneath the mouse
    mark_pixel_with_colour(coords, colour_index) {
        var ctx = this.canvas.getContext("2d");

        // Disable anti-aliasing
        ctx.translate(0.5, 0.5);

        ctx.fillStyle = palette[colour_index];
        ctx.fillRect(
            (coords[0] * this.pixel_size) + (this.pixel_size / 3),
            (coords[1] * this.pixel_size) + (this.pixel_size / 3),
            (this.pixel_size / 3),
            (this.pixel_size / 3)
        );

        // Re-enable anti-aliasing
        ctx.translate(-0.5, -0.5);
    }

    // Set the colour of a pixel
    set_pixel_colour(coords, colour_index) {
        var [x, y] = coords;
        this.image[y][x] = colour_index;
    }

    // Return the colour of a pixel
    get_pixel_colour(coords) {
        var [x, y] = coords;
        return this.image[y][x];
    }

    // Render a single pixel on the canvas. Helper function for render().
    draw_pixel(coords, colour_index) {
        var [x, y] = coords;
        var ctx = this.canvas.getContext("2d");
        ctx.fillStyle = palette[colour_index];
        ctx.fillRect(x * this.pixel_size, y * this.pixel_size, this.pixel_size, this.pixel_size);
    }

    // Redraw the full image on the canvas
    render() {
        for (var y = 0; y < this.height; y++) {
            for (var x = 0; x < this.width; x++) {
                this.draw_pixel([x, y], this.image[y][x]);
            }
        }
    }

    // Convert a mouse event to the coordinates of a pixel
    event_to_pixels(event) {
        var [x, y] = [event.offsetX, event.offsetY];
        var pxl_coords = this.coord_to_pixels([x, y]);
        return pxl_coords;
    }

    // Convert canvas coordinates to pixel coordinates 
    coord_to_pixels(coords) {
        var pxl_x = Math.trunc(coords[0] / this.pixel_size);
        var pxl_y = Math.trunc(coords[1] / this.pixel_size);
        return [pxl_x, pxl_y]
    }
}

class PaintController {
    constructor(profile_image, colour_palette) {
        this.profile_image = profile_image;
        this.profile_image.canvas.addEventListener('click', this.onclick.bind(this), false);
        this.profile_image.canvas.addEventListener('auxclick', this.onauxclick.bind(this), false);
        this.profile_image.canvas.addEventListener('mousemove', this.onhover.bind(this), false);
        this.profile_image.canvas.addEventListener('mouseout', this.mouseout.bind(this), false);

        this.colour_palette = colour_palette;
    }

    get_paint_colour() {
        return this.colour_palette.selected_colour;
    }

    mouseout(event) {
        // Removes last highlight when mouse leaves canvas
        this.profile_image.render();
    }

    paint_pixel(coords, colour_index) {
        this.profile_image.set_pixel_colour(coords, colour_index);
        this.profile_image.render();
    }

    onclick(event) {
        var coords = this.profile_image.event_to_pixels(event);
        this.paint_pixel(coords, this.get_paint_colour());
        this.onhover(event);
    }

    onauxclick(event) {
        var coords = this.profile_image.event_to_pixels(event);
        var clicked_colour = this.profile_image.get_pixel_colour(coords);
        this.colour_palette.set_colour(clicked_colour);
        this.onhover(event);
    }

    onhover(event) {
        var coords = this.profile_image.event_to_pixels(event);
        this.profile_image.render();
        if (event.buttons == 1) {
            this.paint_pixel(coords, this.get_paint_colour());
        }
        this.profile_image.outline_pixel(coords, 11);
        this.profile_image.mark_pixel_with_colour(coords, this.get_paint_colour());
    }
}

class ColourPalette extends ProfileImage {
    constructor(image_canvas, width, height, profile_image_element) {
        super(image_canvas, width, height);
        this.selected_colour = 0;
        this.draw_palette(palette);
        this.canvas.addEventListener('mousemove', this.onhover.bind(this), false)
        this.canvas.addEventListener('mouseout', this.mouseout.bind(this), false)
        this.canvas.addEventListener('click', this.onclick.bind(this), false)
    }

    set_colour(colour_index) {
        this.selected_colour = colour_index;
        this.render();
    }

    mouseout() {
        this.render();
    }

    index_to_coords(index) {
        var y = 0;
        if (index >= 8) {
            y = 1;
        };
        var x = index % 8;
        return [x, y];
    }

    render() {
        super.render();
        var colour = 11
        this.mark_pixel_with_colour(this.index_to_coords(this.selected_colour), colour);
    }

    onhover(event) {
        var coords = this.event_to_pixels(event);
        this.render();
        this.outline_pixel(coords, 12, 4);
    }

    onclick(event) {
        var coords = this.event_to_pixels(event);
        this.selected_colour = this.get_pixel_colour(coords);
        this.render();
        // this.highlight_pixel(coords);
    }

    draw_palette(palette) {
        var i = 0
        for (i; i < palette.length; i++) {
            this.set_pixel_colour(this.index_to_coords(i), i);
        }
        this.render();

    }
}

// Internet explorer icon

// var b64_string = "zMzMzMzGZmzMzMx3ZmbMxszMdmZmVWzGzMdtVmVVVsbMemxmd2zFbMymJmbMdsxsx/h2bMzHxVbNx2ZmZlVVVtwXZmZmZmZm0Wd2bMzMzMyvd3ZszMdmZqZ3d2bMdmZmp853dmZmZmzXzOd3ZmZmzMdsyud3ZszMzHd8zMzMzMw="

// var image_canvas = document.getElementById("paint-canvas");
// var palette_canvas = document.getElementById("paint-palette");
// var b64_element = document.getElementById("hex-field");

// var profile_image = new ProfileImage(16, 16, 32, image_canvas, default_colour = 12);
// profile_image.from_base64(b64_string);
// var colour_palette = new ColourPalette(8, 2, 64, palette_canvas, default_colour = 0);
// var paint_controller = new PaintController(profile_image, colour_palette, b64_element);

// profile_image.render();

function initialise_palette() {
    var palette_canvas = document.getElementById("palette");
    var new_profile_image = document.getElementById("new-profile-image");

    palette_canvas.palette = new ColourPalette(palette_canvas, 8, 2, new_profile_image);
    paint_controller = new PaintController(new_profile_image.profile_image, palette_canvas.palette)
}

function initialise_profile_image(canvas_element) {
    canvas_element.profile_image = new ProfileImage(canvas_element);
}