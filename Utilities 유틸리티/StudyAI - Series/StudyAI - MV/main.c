/*
 * StudyAI - MV (Minimum Viable) - Premium Edition
 * Modern AI Chat Application using GTK3 + libcurl + cJSON + Cairo
 * Features: Streaming, Markdown Rendering, Threading
 * Rheehose (Rhee Creative) 2008-2026
 * Licensed under Apache-2.0
 */

#include <gtk/gtk.h>
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

// UI Widgets
GtkWidget *main_window;
GtkWidget *stack;
GtkWidget *chat_list_box;
GtkWidget *prompt_entry;
GtkWidget *scrolled_window;
GtkWidget *current_bot_label = NULL; // Pointer to the current bot message label for streaming updates
GString *current_bot_text = NULL;    // Buffer for raw bot response

int is_dark_mode = 0;
volatile int is_streaming = 0; // Simple flag to prevent concurrent requests

// Data structures
struct ThreadData {
    char *user_input;
};

// --- Helper Functions ---

// Simple Markdown to Pango Markup Converter
// Supports: **bold**, *italic*, `code`
char* markdown_to_pango(const char *text) {
    GString *out = g_string_new("");
    int len = strlen(text);
    int in_bold = 0;
    int in_italic = 0;
    int in_code = 0;

    for (int i = 0; i < len; i++) {
        // Handle Code (backtick)
        if (text[i] == '`') {
            if (in_code) {
                g_string_append(out, "</tt></span>");
                in_code = 0;
            } else {
                g_string_append(out, "<span background=\"#444444\" foreground=\"#ffffff\"><tt>");
                in_code = 1;
            }
            continue;
        }
        
        if (in_code) {
            // Inside code, escape minimal chars
            if (text[i] == '<') g_string_append(out, "&lt;");
            else if (text[i] == '&') g_string_append(out, "&amp;");
            else g_string_append_c(out, text[i]);
            continue;
        }

        // Handle Bold (**)
        if (i + 1 < len && text[i] == '*' && text[i+1] == '*') {
            if (in_bold) {
                g_string_append(out, "</b>");
                in_bold = 0;
            } else {
                g_string_append(out, "<b>");
                in_bold = 1;
            }
            i++; // Skip second *
            continue;
        }

        // Handle Italic (*)
        if (text[i] == '*') {
            if (in_italic) {
                g_string_append(out, "</i>");
                in_italic = 0;
            } else {
                g_string_append(out, "<i>");
                in_italic = 1;
            }
            continue;
        }

        // Escape XML/Pango special chars
        if (text[i] == '<') g_string_append(out, "&lt;");
        else if (text[i] == '>') g_string_append(out, "&gt;");
        else if (text[i] == '&') g_string_append(out, "&amp;");
        else g_string_append_c(out, text[i]);
    }
    
    // Close any open tags
    if (in_code) g_string_append(out, "</tt></span>");
    if (in_bold) g_string_append(out, "</b>");
    if (in_italic) g_string_append(out, "</i>");

    return g_string_free(out, FALSE);
}

// UI Update Callback for Streaming
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
    return FALSE; // Remove source
}

// Curl Write Callback for Streaming
size_t StreamCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    char *data = malloc(realsize + 1);
    memcpy(data, contents, realsize);
    data[realsize] = 0;

    // Mistral Stream Format: "data: {json}\n\n"
    // Multiple chunks can arrive at once.
    char *line = strtok(data, "\n");
    while (line != NULL) {
        if (strncmp(line, "data: ", 6) == 0) {
            const char *json_str = line + 6;
            if (strcmp(json_str, "[DONE]") == 0) {
                // Stream finished
                break;
            }
            
            cJSON *json = cJSON_Parse(json_str);
            if (json) {
                cJSON *choices = cJSON_GetObjectItemCaseSensitive(json, "choices");
                if (cJSON_IsArray(choices)) {
                    cJSON *choice = cJSON_GetArrayItem(choices, 0);
                    cJSON *delta = cJSON_GetObjectItemCaseSensitive(choice, "delta");
                    if (delta) {
                        cJSON *content = cJSON_GetObjectItemCaseSensitive(delta, "content");
                        if (cJSON_IsString(content)) {
                            // Schedule UI update
                            char *content_chunk = strdup(content->valuestring);
                            g_idle_add(update_bot_message, content_chunk);
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

// --- Drawing Functions (Cairo) ---
// (Same drawing functions as before, omitted for brevity if unchanged, but included here for completeness)

gboolean draw_bot_avatar(GtkWidget *widget, cairo_t *cr, gpointer data) {
    guint width = gtk_widget_get_allocated_width(widget);
    guint height = gtk_widget_get_allocated_height(widget);
    
    // Gradient Background
    cairo_pattern_t *pat = cairo_pattern_create_linear(0.0, 0.0, width, height);
    cairo_pattern_add_color_stop_rgb(pat, 0.0, 0.2, 0.6, 1.0); // Royal Blue
    cairo_pattern_add_color_stop_rgb(pat, 1.0, 0.4, 0.2, 0.8); // Purple
    cairo_set_source(cr, pat);
    cairo_arc(cr, width/2.0, height/2.0, width/2.0 - 2, 0, 2 * G_PI);
    cairo_fill(cr);
    cairo_pattern_destroy(pat);

    // Robot Eyes
    cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);
    cairo_rectangle(cr, width*0.3, height*0.4, width*0.15, height*0.15);
    cairo_rectangle(cr, width*0.55, height*0.4, width*0.15, height*0.15);
    cairo_fill(cr);
    
    return FALSE;
}

gboolean draw_user_avatar(GtkWidget *widget, cairo_t *cr, gpointer data) {
    guint width = gtk_widget_get_allocated_width(widget);
    guint height = gtk_widget_get_allocated_height(widget);
    
    cairo_pattern_t *pat = cairo_pattern_create_linear(0.0, 0.0, width, height);
    cairo_pattern_add_color_stop_rgb(pat, 0.0, 0.1, 0.8, 0.3); // Emerald
    cairo_pattern_add_color_stop_rgb(pat, 1.0, 0.1, 0.9, 0.5); // Teal
    cairo_set_source(cr, pat);
    cairo_arc(cr, width/2.0, height/2.0, width/2.0 - 2, 0, 2 * G_PI);
    cairo_fill(cr);
    cairo_pattern_destroy(pat);

    cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);
    cairo_arc(cr, width/2.0, height*0.4, width*0.2, 0, 2 * G_PI);
    cairo_fill(cr);
    cairo_arc(cr, width/2.0, height*1.0, width*0.35, G_PI, 2 * G_PI);
    cairo_fill(cr);

    return FALSE;
}

gboolean draw_logo(GtkWidget *widget, cairo_t *cr, gpointer data) {
    guint width = gtk_widget_get_allocated_width(widget);
    guint height = gtk_widget_get_allocated_height(widget);
    
    cairo_set_line_width(cr, 4.0);
    cairo_set_source_rgba(cr, 0.4, 0.4, 1.0, 0.8);
    
    cairo_save(cr);
    cairo_translate(cr, width/2.0, height/2.0);
    cairo_scale(cr, 1.0, 0.3);
    cairo_arc(cr, 0, 0, width/3.0, 0, 2 * G_PI);
    cairo_stroke(cr);
    cairo_restore(cr);

    cairo_save(cr);
    cairo_translate(cr, width/2.0, height/2.0);
    cairo_rotate(cr, G_PI/3);
    cairo_scale(cr, 1.0, 0.3);
    cairo_arc(cr, 0, 0, width/3.0, 0, 2 * G_PI);
    cairo_stroke(cr);
    cairo_restore(cr);

    cairo_save(cr);
    cairo_translate(cr, width/2.0, height/2.0);
    cairo_rotate(cr, -G_PI/3);
    cairo_scale(cr, 1.0, 0.3);
    cairo_arc(cr, 0, 0, width/3.0, 0, 2 * G_PI);
    cairo_stroke(cr);
    cairo_restore(cr);
    
    cairo_set_source_rgba(cr, 1.0, 0.6, 0.2, 0.9);
    cairo_arc(cr, width/2.0, height/2.0, width/10.0, 0, 2 * G_PI);
    cairo_fill(cr);

    return FALSE;
}

// --- UI Logic ---

GtkWidget* add_message_bubble(const char *text, int is_user) {
    GtkWidget *row_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    
    GtkWidget *avatar = gtk_drawing_area_new();
    gtk_widget_set_size_request(avatar, 36, 36);
    g_signal_connect(avatar, "draw", G_CALLBACK(is_user ? draw_user_avatar : draw_bot_avatar), NULL);
    
    GtkWidget *bubble_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    GtkWidget *label = gtk_label_new(text);
    gtk_label_set_line_wrap(GTK_LABEL(label), TRUE);
    gtk_label_set_max_width_chars(GTK_LABEL(label), 50); // Wider bubbles
    gtk_label_set_xalign(GTK_LABEL(label), 0.0);
    gtk_label_set_selectable(GTK_LABEL(label), TRUE);
    
    // Use markup for the initial text (even empty)
    if (text && strlen(text) > 0) {
       char *markup = markdown_to_pango(text);
       gtk_label_set_markup(GTK_LABEL(label), markup);
       g_free(markup);
    }

    gtk_container_add(GTK_CONTAINER(bubble_box), label);
    gtk_widget_set_margin_top(bubble_box, 5);
    gtk_widget_set_margin_bottom(bubble_box, 5);
    gtk_widget_set_margin_start(bubble_box, 10);
    gtk_widget_set_margin_end(bubble_box, 10);
    
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
    
    gtk_list_box_insert(GTK_LIST_BOX(chat_list_box), row_box, -1);
    gtk_widget_show_all(row_box);
    
    return label;
}

gboolean completion_finished(gpointer data) {
    is_streaming = 0;
    gtk_widget_set_sensitive(prompt_entry, TRUE); // Re-enable input
    return FALSE;
}

void *api_thread_func(void *data) {
    struct ThreadData *tdata = (struct ThreadData *)data;
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if(curl) {
        cJSON *root = cJSON_CreateObject();
        cJSON_AddStringToObject(root, "model", MODEL_NAME);
        cJSON_AddBoolToObject(root, "stream", cJSON_True); // Enable Streaming
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
        
        // Ignore SSL verification for simplicity if needed (not recommended but for MV compatibility)
        // curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);

        res = curl_easy_perform(curl);
        
        if(res != CURLE_OK) {
             // Handle error - maybe via another idle callback
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        cJSON_Delete(root);
        free(json_str);
    }
    
    free(tdata->user_input);
    free(tdata);
    
    // Signal completion on main thread
    g_idle_add(completion_finished, NULL);
    
    pthread_exit(NULL);
    return NULL;
}

void on_send_clicked(GtkWidget *widget, gpointer data) {
    if (is_streaming) return;

    const char *text = gtk_entry_get_text(GTK_ENTRY(prompt_entry));
    if (strlen(text) > 0) {
        gtk_stack_set_visible_child_name(GTK_STACK(stack), "chat_view");
        
        // User Message
        add_message_bubble(text, 1);
        
        // Prepare Bot Message Bubble
        if (current_bot_text) g_string_free(current_bot_text, TRUE);
        current_bot_text = g_string_new("");
        current_bot_label = add_message_bubble("", 0); // Empty bubble for bot
        
        // Disable input
        is_streaming = 1;
        gtk_widget_set_sensitive(prompt_entry, FALSE);
        
        // Start Thread
        struct ThreadData *tdata = malloc(sizeof(struct ThreadData));
        tdata->user_input = strdup(text);
        
        pthread_t thread_id;
        pthread_create(&thread_id, NULL, api_thread_func, (void *)tdata);
        pthread_detach(thread_id); // Don't need to join, it manages itself
        
        gtk_entry_set_text(GTK_ENTRY(prompt_entry), "");
    }
}

// Theme Handling
void set_theme(int dark) {
    GtkCssProvider *provider = gtk_css_provider_new();
    const char *css;
    
    if (dark) {
        css = 
        "window { background-color: #121212; color: #ffffff; }"
        "list { background-color: #121212; }"
        ".message-bubble { padding: 10px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }"
        ".user-bubble { background-image: linear-gradient(to right, #2b5876, #4e4376); color: white; margin-left: 50px; }"
        ".bot-bubble { background-color: #2d2d2d; color: #e0e0e0; margin-right: 50px; border: 1px solid #333; }"
        "entry { background-color: #2d2d2d; color: white; border-radius: 20px; border: 1px solid #444; padding: 5px 10px; }"
        "button.send-btn { background-image: linear-gradient(to right, #11998e, #38ef7d); color: white; border-radius: 20px; font-weight: bold; border: none; }"
        "label.title { font-size: 24px; font-weight: bold; color: #38ef7d; }"
        "label.subtitle { font-size: 14px; color: #888; }";
    } else {
        css = 
        "window { background-color: #f5f7fa; color: #333; }"
        "list { background-color: #f5f7fa; }"
        ".message-bubble { padding: 10px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }"
        ".user-bubble { background-image: linear-gradient(to right, #00c6ff, #0072ff); color: white; margin-left: 50px; }"
        ".bot-bubble { background-color: white; color: #333; margin-right: 50px; border: 1px solid #ddd; }"
        "entry { background-color: white; color: black; border-radius: 20px; border: 1px solid #ddd; padding: 5px 10px; }"
        "button.send-btn { background-image: linear-gradient(to right, #11998e, #38ef7d); color: white; border-radius: 20px; font-weight: bold; border: none; }"
        "label.title { font-size: 24px; font-weight: bold; color: #2c3e50; }"
        "label.subtitle { font-size: 14px; color: #7f8c8d; }";
    }
    
    gtk_css_provider_load_from_data(provider, css, -1, NULL);
    GdkScreen *screen = gdk_screen_get_default();
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(provider);
}

void on_toggle_theme(GtkWidget *widget, gpointer data) {
    is_dark_mode = !is_dark_mode;
    set_theme(is_dark_mode);
    gtk_button_set_label(GTK_BUTTON(widget), is_dark_mode ? "☀️" : "🌙");
}

int main(int argc, char *argv[]) {
    // Init GThread for thread safety in GTK
    gdk_threads_init(); // Deprecated in newer GTK but good for GTK3 compat
    gtk_init(&argc, &argv);

    main_window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(main_window), "StudyAI - Premium");
    gtk_window_set_default_size(GTK_WINDOW(main_window), 450, 700);
    g_signal_connect(main_window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    GtkWidget *main_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_container_add(GTK_CONTAINER(main_window), main_vbox);

    // -- Header --
    GtkWidget *header = gtk_header_bar_new();
    gtk_header_bar_set_show_close_button(GTK_HEADER_BAR(header), TRUE);
    gtk_header_bar_set_title(GTK_HEADER_BAR(header), "StudyAI");
    gtk_header_bar_set_subtitle(GTK_HEADER_BAR(header), "Powered by Mistral");
    gtk_window_set_titlebar(GTK_WINDOW(main_window), header);

    GtkWidget *theme_btn = gtk_button_new_with_label("🌙");
    g_signal_connect(theme_btn, "clicked", G_CALLBACK(on_toggle_theme), NULL);
    gtk_header_bar_pack_end(GTK_HEADER_BAR(header), theme_btn);

    // -- Stack --
    stack = gtk_stack_new();
    gtk_stack_set_transition_type(GTK_STACK(stack), GTK_STACK_TRANSITION_TYPE_SLIDE_LEFT);
    gtk_box_pack_start(GTK_BOX(main_vbox), stack, TRUE, TRUE, 0);

    // 1. Start View
    GtkWidget *start_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 20);
    gtk_widget_set_valign(start_vbox, GTK_ALIGN_CENTER);
    
    GtkWidget *logo_drawing = gtk_drawing_area_new();
    gtk_widget_set_size_request(logo_drawing, 120, 120);
    gtk_widget_set_halign(logo_drawing, GTK_ALIGN_CENTER);
    g_signal_connect(logo_drawing, "draw", G_CALLBACK(draw_logo), NULL);
    
    GtkWidget *title_label = gtk_label_new("StudyAI");
    gtk_style_context_add_class(gtk_widget_get_style_context(title_label), "title");
    
    GtkWidget *subtitle_label = gtk_label_new("Your Intelligent Companion\nAsk me anything.");
    gtk_style_context_add_class(gtk_widget_get_style_context(subtitle_label), "subtitle");
    gtk_label_set_justify(GTK_LABEL(subtitle_label), GTK_JUSTIFY_CENTER);

    gtk_box_pack_start(GTK_BOX(start_vbox), logo_drawing, FALSE, FALSE, 0);
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

    // -- Input --
    GtkWidget *input_area = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_widget_set_margin_start(input_area, 10);
    gtk_widget_set_margin_end(input_area, 10);
    gtk_widget_set_margin_bottom(input_area, 10);
    gtk_widget_set_margin_top(input_area, 10);

    prompt_entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(prompt_entry), "Message StudyAI...");
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
