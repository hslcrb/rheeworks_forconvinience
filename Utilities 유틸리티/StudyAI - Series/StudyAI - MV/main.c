/*
 * StudyAI - MV (Minimum Viable) - Ultra Premium Edition
 * Modern AI Chat Application with SVG Graphics & Smooth Animations
 * Rheehose (Rhee Creative) 2008-2026
 * Licensed under Apache-2.0
 */

#include <gtk/gtk.h>
#include <librsvg/rsvg.h>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include "cJSON.h"

// API Configuration
#define MISTRAL_API_KEY "OBfwuYKEEUFvjh5bLt18XOcVIpTYFHVQ"
#define MISTRAL_API_URL "https://api.mistral.ai/v1/chat/completions"
#define MODEL_NAME "mistral-small-latest"

// SVG Icons (Inline)
const char *SVG_BOT_AVATAR = 
"<svg width='40' height='40' viewBox='0 0 40 40'>"
"<defs>"
"<linearGradient id='botGrad' x1='0%' y1='0%' x2='100%' y2='100%'>"
"<stop offset='0%' style='stop-color:#667eea;stop-opacity:1'/>"
"<stop offset='100%' style='stop-color:#764ba2;stop-opacity:1'/>"
"</linearGradient>"
"</defs>"
"<circle cx='20' cy='20' r='19' fill='url(#botGrad)'/>"
"<rect x='11' y='14' width='6' height='6' rx='1' fill='white'/>"
"<rect x='23' y='14' width='6' height='6' rx='1' fill='white'/>"
"<path d='M 12 26 Q 20 30 28 26' stroke='white' stroke-width='2' fill='none' stroke-linecap='round'/>"
"</svg>";

const char *SVG_USER_AVATAR = 
"<svg width='40' height='40' viewBox='0 0 40 40'>"
"<defs>"
"<linearGradient id='userGrad' x1='0%' y1='0%' x2='100%' y2='100%'>"
"<stop offset='0%' style='stop-color:#11998e;stop-opacity:1'/>"
"<stop offset='100%' style='stop-color:#38ef7d;stop-opacity:1'/>"
"</linearGradient>"
"</defs>"
"<circle cx='20' cy='20' r='19' fill='url(#userGrad)'/>"
"<circle cx='20' cy='15' r='6' fill='white'/>"
"<path d='M 8 32 Q 20 28 32 32 L 32 36 Q 20 32 8 36 Z' fill='white'/>"
"</svg>";

const char *SVG_LOGO = 
"<svg width='150' height='150' viewBox='0 0 150 150'>"
"<defs>"
"<linearGradient id='logoGrad1' x1='0%' y1='0%' x2='100%' y2='100%'>"
"<stop offset='0%' style='stop-color:#667eea;stop-opacity:0.9'/>"
"<stop offset='100%' style='stop-color:#764ba2;stop-opacity:0.9'/>"
"</linearGradient>"
"<radialGradient id='logoGrad2'>"
"<stop offset='0%' style='stop-color:#f093fb;stop-opacity:1'/>"
"<stop offset='100%' style='stop-color:#f5576c;stop-opacity:1'/>"
"</radialGradient>"
"</defs>"
"<g transform='translate(75,75)'>"
"<ellipse rx='50' ry='15' transform='rotate(0)' stroke='url(#logoGrad1)' stroke-width='3' fill='none'/>"
"<ellipse rx='50' ry='15' transform='rotate(60)' stroke='url(#logoGrad1)' stroke-width='3' fill='none'/>"
"<ellipse rx='50' ry='15' transform='rotate(120)' stroke='url(#logoGrad1)' stroke-width='3' fill='none'/>"
"<circle r='12' fill='url(#logoGrad2)'/>"
"<circle r='5' fill='white' opacity='0.8'/>"
"</g>"
"</svg>";

// UI Widgets
GtkWidget *main_window;
GtkWidget *stack;
GtkWidget *chat_list_box;
GtkWidget *prompt_entry;
GtkWidget *scrolled_window;
GtkWidget *current_bot_label = NULL;
GString *current_bot_text = NULL;

int is_dark_mode = 0;
volatile int is_streaming = 0;

struct ThreadData {
    char *user_input;
};

// --- SVG Helper Functions ---

GdkPixbuf* svg_to_pixbuf(const char *svg_data, int width, int height) {
    GError *error = NULL;
    RsvgHandle *handle = rsvg_handle_new_from_data((const guint8*)svg_data, strlen(svg_data), &error);
    if (!handle) {
        if (error) {
            g_error_free(error);
        }
        return NULL;
    }
    
    GdkPixbuf *pixbuf = rsvg_handle_get_pixbuf_sub(handle, NULL);
    g_object_unref(handle);
    
    if (pixbuf && (width != -1 || height != -1)) {
        GdkPixbuf *scaled = gdk_pixbuf_scale_simple(pixbuf, width, height, GDK_INTERP_BILINEAR);
        g_object_unref(pixbuf);
        return scaled;
    }
    
    return pixbuf;
}

// --- Markdown Parser (same as before) ---

char* markdown_to_pango(const char *text) {
    GString *out = g_string_new("");
    int len = strlen(text);
    int in_bold = 0, in_italic = 0, in_code = 0;

    for (int i = 0; i < len; i++) {
        if (text[i] == '`') {
            if (in_code) {
                g_string_append(out, "</tt></span>");
                in_code = 0;
            } else {
                g_string_append(out, "<span background='#444' foreground='#fff'><tt>");
                in_code = 1;
            }
            continue;
        }
        
        if (in_code) {
            if (text[i] == '<') g_string_append(out, "&lt;");
            else if (text[i] == '&') g_string_append(out, "&amp;");
            else g_string_append_c(out, text[i]);
            continue;
        }

        if (i + 1 < len && text[i] == '*' && text[i+1] == '*') {
            in_bold = !in_bold;
            g_string_append(out, in_bold ? "<b>" : "</b>");
            i++;
            continue;
        }

        if (text[i] == '*') {
            in_italic = !in_italic;
            g_string_append(out, in_italic ? "<i>" : "</i>");
            continue;
        }

        if (text[i] == '<') g_string_append(out, "&lt;");
        else if (text[i] == '>') g_string_append(out, "&gt;");
        else if (text[i] == '&') g_string_append(out, "&amp;");
        else g_string_append_c(out, text[i]);
    }
    
    if (in_code) g_string_append(out, "</tt></span>");
    if (in_bold) g_string_append(out, "</b>");
    if (in_italic) g_string_append(out, "</i>");

    return g_string_free(out, FALSE);
}

// --- Streaming Callbacks ---

gboolean update_bot_message(gpointer user_data) {
    char *chunk = (char *)user_data;
    if (current_bot_text) {
        g_string_append(current_bot_text, chunk);
        if (current_bot_label) {
            char *markup = markdown_to_pango(current_bot_text->str);
            gtk_label_set_markup(GTK_LABEL(current_bot_label), markup);
            g_free(markup);
        }
    }
    free(chunk);
    return FALSE;
}

size_t StreamCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    char *data = malloc(realsize + 1);
    memcpy(data, contents, realsize);
    data[realsize] = 0;

    char *line = strtok(data, "\n");
    while (line != NULL) {
        if (strncmp(line, "data: ", 6) == 0) {
            const char *json_str = line + 6;
            if (strcmp(json_str, "[DONE]") == 0) break;
            
            cJSON *json = cJSON_Parse(json_str);
            if (json) {
                cJSON *choices = cJSON_GetObjectItemCaseSensitive(json, "choices");
                if (cJSON_IsArray(choices)) {
                    cJSON *choice = cJSON_GetArrayItem(choices, 0);
                    cJSON *delta = cJSON_GetObjectItemCaseSensitive(choice, "delta");
                    if (delta) {
                        cJSON *content = cJSON_GetObjectItemCaseSensitive(delta, "content");
                        if (cJSON_IsString(content)) {
                            g_idle_add(update_bot_message, strdup(content->valuestring));
                        }
                    }
                }
                cJSON_Delete(json);
            }
        }
        line = strtok(NULL, "\n");
    }

    free(data);
    return realsize;
}

// --- UI Components ---

GtkWidget* create_svg_image(const char *svg_data, int size) {
    GdkPixbuf *pixbuf = svg_to_pixbuf(svg_data, size, size);
    GtkWidget *image = gtk_image_new_from_pixbuf(pixbuf);
    if (pixbuf) g_object_unref(pixbuf);
    return image;
}

GtkWidget* add_message_bubble(const char *text, int is_user) {
    GtkWidget *row_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    gtk_widget_set_margin_top(row_box, 8);
    gtk_widget_set_margin_bottom(row_box, 8);
    
    GtkWidget *avatar = create_svg_image(is_user ? SVG_USER_AVATAR : SVG_BOT_AVATAR, 40);
    
    GtkWidget *bubble_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    GtkWidget *label = gtk_label_new(text);
    gtk_label_set_line_wrap(GTK_LABEL(label), TRUE);
    gtk_label_set_max_width_chars(GTK_LABEL(label), 50);
    gtk_label_set_xalign(GTK_LABEL(label), 0.0);
    gtk_label_set_selectable(GTK_LABEL(label), TRUE);
    
    if (text && strlen(text) > 0) {
       char *markup = markdown_to_pango(text);
       gtk_label_set_markup(GTK_LABEL(label), markup);
       g_free(markup);
    }

    gtk_container_add(GTK_CONTAINER(bubble_box), label);
    gtk_widget_set_margin_top(bubble_box, 12);
    gtk_widget_set_margin_bottom(bubble_box, 12);
    gtk_widget_set_margin_start(bubble_box, 16);
    gtk_widget_set_margin_end(bubble_box, 16);
    
    GtkStyleContext *context = gtk_widget_get_style_context(bubble_box);
    gtk_style_context_add_class(context, "message-bubble");
    gtk_style_context_add_class(context, is_user ? "user-bubble" : "bot-bubble");
    
    if (is_user) {
        gtk_box_pack_end(GTK_BOX(row_box), avatar, FALSE, FALSE, 0);
        gtk_box_pack_end(GTK_BOX(row_box), bubble_box, FALSE, FALSE, 0);
        gtk_widget_set_halign(row_box, GTK_ALIGN_END);
    } else {
        gtk_box_pack_start(GTK_BOX(row_box), avatar, FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(row_box), bubble_box, FALSE, FALSE, 0);
        gtk_widget_set_halign(row_box, GTK_ALIGN_START);
    }
    
    gtk_widget_set_margin_start(row_box, 20);
    gtk_widget_set_margin_end(row_box, 20);
    
    gtk_list_box_insert(GTK_LIST_BOX(chat_list_box), row_box, -1);
    gtk_widget_show_all(row_box);
    
    return label;
}

gboolean completion_finished(gpointer data) {
    is_streaming = 0;
    gtk_widget_set_sensitive(prompt_entry, TRUE);
    return FALSE;
}

void *api_thread_func(void *data) {
    struct ThreadData *tdata = (struct ThreadData *)data;
    CURL *curl = curl_easy_init();
    
    if(curl) {
        cJSON *root = cJSON_CreateObject();
        cJSON_AddStringToObject(root, "model", MODEL_NAME);
        cJSON_AddBoolToObject(root, "stream", cJSON_True);
        cJSON *messages = cJSON_CreateArray();
        cJSON *msg = cJSON_CreateObject();
        cJSON_AddStringToObject(msg, "role", "user");
        cJSON_AddStringToObject(msg, "content", tdata->user_input);
        cJSON_AddItemToArray(messages, msg);
        cJSON_AddItemToObject(root, "messages", messages);
        
        char *json_str = cJSON_PrintUnformatted(root);
        
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        char auth_header[256];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", MISTRAL_API_KEY);
        headers = curl_slist_append(headers, auth_header);

        curl_easy_setopt(curl, CURLOPT_URL, MISTRAL_API_URL);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, StreamCallback);
        
        curl_easy_perform(curl);
        
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        cJSON_Delete(root);
        free(json_str);
    }
    
    free(tdata->user_input);
    free(tdata);
    g_idle_add(completion_finished, NULL);
    pthread_exit(NULL);
}

void on_send_clicked(GtkWidget *widget, gpointer data) {
    if (is_streaming) return;

    const char *text = gtk_entry_get_text(GTK_ENTRY(prompt_entry));
    if (strlen(text) > 0) {
        // Smooth transition to chat view
        gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_SLIDE_LEFT);
        gtk_stack_set_transition_duration(GTK_STACK(stack), 300);
        gtk_stack_set_visible_child_name(GTK_STACK(stack), "chat_view");
        
        add_message_bubble(text, 1);
        
        if (current_bot_text) g_string_free(current_bot_text, TRUE);
        current_bot_text = g_string_new("");
        current_bot_label = add_message_bubble("", 0);
        
        is_streaming = 1;
        gtk_widget_set_sensitive(prompt_entry, FALSE);
        
        struct ThreadData *tdata = malloc(sizeof(struct ThreadData));
        tdata->user_input = strdup(text);
        
        pthread_t thread_id;
        pthread_create(&thread_id, NULL, api_thread_func, (void *)tdata);
        pthread_detach(thread_id);
        
        gtk_entry_set_text(GTK_ENTRY(prompt_entry), "");
    }
}

void set_theme(int dark) {
    GtkCssProvider *provider = gtk_css_provider_new();
    const char *css;
    
    if (dark) {
        css = 
        "window { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; }"
        "list { background: transparent; }"
        ".message-bubble { padding: 14px 18px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: all 0.2s; }"
        ".message-bubble:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.5); }"
        ".user-bubble { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }"
        ".bot-bubble { background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); color: #e0e0e0; border: 1px solid rgba(255,255,255,0.1); }"
        "entry { background: rgba(255,255,255,0.1); color: white; border-radius: 24px; border: 1px solid rgba(255,255,255,0.2); padding: 12px 20px; font-size: 14px; }"
        "entry:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.3); }"
        "button.send-btn { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; border-radius: 24px; font-weight: 600; border: none; padding: 12px 28px; transition: all 0.3s; }"
        "button.send-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56,239,125,0.4); }"
        "label.title { font-size: 42px; font-weight: 700; color: #fff; text-shadow: 0 4px 20px rgba(102,126,234,0.5); }"
        "label.subtitle { font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 300; letter-spacing: 0.5px; }";
    } else {
        css = 
        "window { background: linear-gradient(135deg, #ffecd2, #fcb69f); color: #333; }"
        "list { background: transparent; }"
        ".message-bubble { padding: 14px 18px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s; }"
        ".message-bubble:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }"
        ".user-bubble { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }"
        ".bot-bubble { background: white; color: #333; border: 1px solid rgba(0,0,0,0.05); }"
        "entry { background: white; color: #333; border-radius: 24px; border: 1px solid rgba(0,0,0,0.1); padding: 12px 20px; font-size: 14px; }"
        "entry:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.2); }"
        "button.send-btn { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; border-radius: 24px; font-weight: 600; border: none; padding: 12px 28px; transition: all 0.3s; }"
        "button.send-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56,239,125,0.3); }"
        "label.title { font-size: 42px; font-weight: 700; color: #333; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }"
        "label.subtitle { font-size: 16px; color: rgba(0,0,0,0.6); font-weight: 300; letter-spacing: 0.5px; }";
    }
    
    gtk_css_provider_load_from_data(provider, css, -1, NULL);
    GdkScreen *screen = gdk_screen_get_default();
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(provider);
}

void on_toggle_theme(GtkWidget *widget, gpointer data) {
    is_dark_mode = !is_dark_mode;
    set_theme(is_dark_mode);
    gtk_button_set_label(GTK_BUTTON(widget), is_dark_mode ? "☀" : "🌙");
}

// Logo Pulse Animation
gboolean pulse_logo(gpointer user_data) {
    static double scale = 1.0;
    static int direction = 1;
    
    GtkWidget *logo = (GtkWidget *)user_data;
    
    scale += direction * 0.02;
    if (scale > 1.1) direction = -1;
    if (scale < 0.95) direction = 1;
    
    // Trigger redraw (simple approach, ideally use CSS animations but this works for MVP)
    gtk_widget_queue_draw(logo);
    
    return TRUE; // Continue animation
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    main_window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(main_window), "StudyAI - Ultra Premium");
    gtk_window_set_default_size(GTK_WINDOW(main_window), 480, 720);
    g_signal_connect(main_window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    GtkWidget *main_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_container_add(GTK_CONTAINER(main_window), main_vbox);

    // Header
    GtkWidget *header = gtk_header_bar_new();
    gtk_header_bar_set_show_close_button(GTK_HEADER_BAR(header), TRUE);
    gtk_header_bar_set_title(GTK_HEADER_BAR(header), "StudyAI");
    gtk_header_bar_set_subtitle(GTK_HEADER_BAR(header), "Powered by Mistral AI");
    gtk_window_set_titlebar(GTK_WINDOW(main_window), header);

    GtkWidget *theme_btn = gtk_button_new_with_label("🌙");
    gtk_widget_set_tooltip_text(theme_btn, "Toggle Theme");
    g_signal_connect(theme_btn, "clicked", G_CALLBACK(on_toggle_theme), NULL);
    gtk_header_bar_pack_end(GTK_HEADER_BAR(header), theme_btn);

    // Stack
    stack = gtk_stack_new();
    gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_CROSSFADE);
    gtk_stack_set_transition_duration(GTK_STACK(stack), 400);
    gtk_box_pack_start(GTK_BOX(main_vbox), stack, TRUE, TRUE, 0);

    // 1. Start View (Refined)
    GtkWidget *start_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 30);
    gtk_widget_set_valign(start_vbox, GTK_ALIGN_CENTER);
    gtk_widget_set_halign(start_vbox, GTK_ALIGN_CENTER);
    
    GtkWidget *logo_image = create_svg_image(SVG_LOGO, 150);
    // Add subtle pulse animation
    g_timeout_add(50, pulse_logo, logo_image);
    
    GtkWidget *title_label = gtk_label_new("StudyAI");
    gtk_style_context_add_class(gtk_widget_get_style_context(title_label), "title");
    
    GtkWidget *subtitle_label = gtk_label_new("Your Intelligent Companion\nPowered by Advanced AI");
    gtk_style_context_add_class(gtk_widget_get_style_context(subtitle_label), "subtitle");
    gtk_label_set_justify(GTK_LABEL(subtitle_label), GTK_JUSTIFY_CENTER);

    gtk_box_pack_start(GTK_BOX(start_vbox), logo_image, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(start_vbox), title_label, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(start_vbox), subtitle_label, FALSE, FALSE, 0);

    gtk_stack_add_named(GTK_STACK(stack), start_vbox, "start_view");

    // 2. Chat View
    scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
    
    chat_list_box = gtk_list_box_new();
    gtk_list_box_set_selection_mode(GTK_LIST_BOX(chat_list_box), GTK_SELECTION_NONE);
    gtk_container_add(GTK_CONTAINER(scrolled_window), chat_list_box);
    
    gtk_stack_add_named(GTK_STACK(stack), scrolled_window, "chat_view");

    // Input Area
    GtkWidget *input_area = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    gtk_widget_set_margin_start(input_area, 20);
    gtk_widget_set_margin_end(input_area, 20);
    gtk_widget_set_margin_bottom(input_area, 20);
    gtk_widget_set_margin_top(input_area, 15);

    prompt_entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(prompt_entry), "Ask me anything...");
    g_signal_connect(prompt_entry, "activate", G_CALLBACK(on_send_clicked), NULL);
    
    GtkWidget *send_btn = gtk_button_new_with_label("Send");
    gtk_style_context_add_class(gtk_widget_get_style_context(send_btn), "send-btn");
    g_signal_connect(send_btn, "clicked", G_CALLBACK(on_send_clicked), NULL);

    gtk_box_pack_start(GTK_BOX(input_area), prompt_entry, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(input_area), send_btn, FALSE, FALSE, 0);

    gtk_box_pack_end(GTK_BOX(main_vbox), input_area, FALSE, FALSE, 0);

    set_theme(0);
    gtk_widget_show_all(main_window);
    gtk_main();

    return 0;
}
